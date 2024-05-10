from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import re
from datetime import datetime



class PleAssetsBook0703(models.Model):
    _inherit = 'ple.report.assets.book'

    def get_data_7_3_active(self):
        query_data = """ 
        CREATE OR REPLACE FUNCTION get_balance(am_id INT, OUT amount_pe FLOAT) AS $$
        BEGIN
        SELECT aml.balance  INTO amount_pe
        FROM account_move am
        LEFT JOIN account_move_line aml ON aml.move_id = am.id
        LEFT JOIN account_account   acc ON acc.id=aml.account_id             
        WHERE 
        am.id = am_id  
        and acc.ple_selection in ('assets_book_acquisition_asset','assets_book_improvements_asset',
        'assets_book_other_asset','assets_book_voluntary_revaluation_asset',
        'assets_book_revaluation_reorganization_asset','assets_book_revaluation_other_asset',
        'assets_book_inflation_asset');
        END;
        $$ 
        LANGUAGE plpgsql;
        
        SELECT  
        aa.id as id,
        am.id as move_id,
        rc.id as res_currency_id,
        COALESCE(am.name,aa.name) AS name,
        COALESCE(aml.ple_correlative,'M000000001') as ple_correlative,
        aa.asset_catalog_code as asset_catalog_code,
        COALESCE(aa.asset_code,'SC01') as asset_code,
        aa.state as state,
        CASE WHEN aa.disposal_date is not null and aa.disposal_date >= '{date_start}' and aa.disposal_date <= '{date_end}' then True else False end as disposal_date,
        TO_CHAR(aa.acquisition_date,'DD/MM/YYYY') as acquisition_date,
        TO_CHAR(am.date,'DD/MM/YYYY') as date,
        aa.acquisition_date as acq_date,
        aa.original_value as original_value,
        acc.ple_selection as ple_selection,
        am.exchange_rate as exchange_rate,
        COALESCE(get_balance(am.id),0.00) as value_acquisition_local
        
        from account_asset  aa
        --This is my connection with original_move_line_ids
        LEFT JOIN asset_move_line_rel amlr  ON  amlr.asset_id=aa.id
        LEFT JOIN account_move_line aml     ON  amlr.line_id=aml.id
        LEFT JOIN account_move am           ON  aml.move_id=am.id        
        
        LEFT JOIN account_account  acc      ON  acc.id=aa.account_asset_id
        LEFT JOIN res_currency rc           ON  aa.currency_id=rc.id
        where 
        (aa.acquisition_date <= '{date_end}')
        AND rc.name !='PEN'
        AND aa.id IS NOT NULL
        AND acc.ple_selection in ('assets_book_acquisition_asset','assets_book_improvements_asset',
        'assets_book_other_asset','assets_book_voluntary_revaluation_asset','assets_book_revaluation_reorganization_asset',
        'assets_book_revaluation_other_asset','assets_book_inflation_asset')
        
        """.format(
            date_start=self.date_start,
            date_end=self.date_end
        )
        try:
            self.env.cr.execute(query_data)
            query_data = self.env.cr.dictfetchall()
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')
        return query_data

    def clean_data(self, data):
        return re.sub(r"[^a-zA-Z0-9]", "", data)

    def _execute_lines_7_3_active(self):
        lines = []
        data_in_bd = self.get_data_7_3_active()
        list_asset_ids = list(map(lambda d: d.get('id', None), data_in_bd))
        data_compute_asset = self.env['account.asset'].search([('id', 'in', list_asset_ids)])
        list_data = self._calculate_columns_AC_to_AD()

        def function_lines_7_3():
            if asset['exchange_rate']:
                foreign_currency_exchange_rate = asset['exchange_rate']
            elif rate_inverse_company_rate:
                foreign_currency_exchange_rate = rate_inverse_company_rate
            else:
                foreign_currency_exchange_rate = rate_inverse_company_rate_max,

            adjust_difference_exchange_rate = 0.00
            if asset['original_value'] and asset['exchange_rate'] and rate_inverse_company_rate_end:
                adjust_difference_exchange_rate = round((asset['original_value'] * asset['exchange_rate']) - (asset['original_value'] * rate_inverse_company_rate_end),2)

            lines.append({
                'id': self.exist_data(asset['id']),

                'period': self.date_start.strftime('%Y0000'),
                'cuo': self.clean_data(asset['name'])[:40],
                'correlative': self.clean_data(asset['ple_correlative']),
                'asset_catalog_code': asset['asset_catalog_code'],
                'asset_code': self.exist_data(asset['asset_code']),

                'acquisition_date': asset['date'],
                'value_acquisition_exchange': "{:.2f}".format(asset['original_value']) if asset['original_value'] else "{:.2f}".format(0),
                'foreign_currency_exchange_rate': "{:.3f}".format(foreign_currency_exchange_rate) if foreign_currency_exchange_rate else "{:.3f}".format(0),
                'value_acquisition_local': "{:.2f}".format(asset['value_acquisition_local']) if asset['value_acquisition_local'] != 0.00 else "{:.2f}".format(asset['original_value'] * foreign_currency_exchange_rate),
                'currency_exchange_rate_3112': "{:.3f}".format(rate_inverse_company_rate_end),

                'adjust_difference_exchange_rate': "{:.2f}".format(adjust_difference_exchange_rate),
                'amount_withdrawals': "{:.2f}".format(-amount_withdrawals) if amount_withdrawals else "{:.2f}".format(0),
                'dep_amount_withdrawals': "{:.2f}".format(0),
                'amount_other_ple': "{:.2f}".format(0),                
            })
            return lines

        rate_inverse_company_rate_end = 0.00
        rate_inverse_company_rate = 0.00
        rate_inverse_company_rate_max = 0.00
        amount_withdrawals = 0.00
        for asset in data_in_bd:
            for var_list in list_data:
                if asset['id'] == var_list['id']:
                    amount_withdrawals = round(var_list['data'][8],2)
                    if self.date_end.year > datetime.now().year:
                        amount_withdrawals = 0.00

            for asset_2 in data_compute_asset:
                if asset['id'] == asset_2.id:
                    for rate_id in asset_2.currency_id.rate_ids:
                        # This is for field inverse_company_rate in currency_id
                        if rate_id.name.year == self.date_end.year and rate_id.name.month == 12 and rate_id.name.day == 31 :
                            rate_inverse_company_rate_end = rate_id.inverse_company_rate

                        if rate_id.name == asset['acq_date']:
                            rate_inverse_company_rate = rate_id.inverse_company_rate

                        if rate_id[0].name:
                            rate_inverse_company_rate_max = rate_id.inverse_company_rate

            function_lines_7_3()
            
            for var_list in list_data:
                if asset['id'] == var_list['id'] and asset['state'] == 'close' and asset['disposal_date']:
                        query = """
                            SELECT 
                                TO_CHAR(am.date,'DD/MM/YYYY') as date,
                                COALESCE(correlative_dep(aa.id,am.id),'M000000001') as correlative,
                                am.name as name
                            FROM account_asset as aa
                            LEFT JOIN account_move am       ON  am.asset_id=aa.id
                            WHERE aa.id = {asset_id}
                            ORDER BY name desc
                            LIMIT 1
                        """.format(asset_id=asset['id'])
                        try:
                            self.env.cr.execute(query)
                            query_data = self.env.cr.dictfetchall()
                        except Exception as error:
                            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')
                                                
                        function_lines_7_3()
                        
                        if len(query_data) != 0:
                            lines[-1].update({
                                'cuo': self.clean_data(query_data[0]['name'])[:40],
                                'correlative': self.clean_data(query_data[0]['correlative']),
                                'acquisition_date': query_data[0]['date'],
                            })
                        
                        lines[-1].update({                            
                            'value_acquisition_exchange': "{:.2f}".format(-asset['original_value']) if asset['original_value'] else "{:.2f}".format(0),
                            'value_acquisition_local': "{:.2f}".format(-asset['value_acquisition_local']) if asset['value_acquisition_local'] else "{:.2f}".format(0),
                            'currency_exchange_rate_3112': "{:.2f}".format(0),
                            'adjust_difference_exchange_rate': "{:.2f}".format(0),
                            'amount_withdrawals': "{:.2f}".format(0),
                            'dep_amount_withdrawals': "{:.2f}".format(0)
                        })
        return lines

    def get_data_7_3_depreciation_sql(self):
        query_data = """

            select
            aa.id as id,
            am.id as move_id,
            am.name as am_name,
            
            ag.code_prefix_start as code_prefix_start,
            COALESCE(correlative_dep(aa.id,am.id),'M000000001') as correlative,
            aa.asset_catalog_code as  asset_catalog_code,
            COALESCE(aa.asset_code,'SC01') as asset_code,
            CASE WHEN aa.disposal_date is not null and aa.disposal_date >= '{start_date}' and aa.disposal_date <= '{date_end}' then True else False end as disposal_date,
            acc.ple_selection as ple_selection,
            TO_CHAR(aa.acquisition_date,'DD/MM/YYYY') as acquisition_date,
            TO_CHAR(am.date,'DD/MM/YYYY') as date,
            amount_total_currency('{start_date}','{date_end}',aa.id,am.id) as amount_total
    
            FROM ACCOUNT_ASSET aa
            LEFT JOIN ACCOUNT_MOVE am       ON  am.asset_id=aa.id
            LEFT JOIN ACCOUNT_ACCOUNT acc    ON  acc.id=aa.account_depreciation_id
            LEFT JOIN ACCOUNT_GROUP  ag      ON  acc.group_id=ag.id  
            LEFT JOIN RES_CURRENCY rc        ON aa.currency_id=rc.id
        
            WHERE
            ('{start_date}'<=am.date and am.date <= '{date_end}') and
            aa.company_id={company_id} and ag.code_prefix_start ='39' and  am.state='posted' and
            rc.name !='PEN'
                """.format(
            start_date=self.date_start,
            date_end=self.date_end,
            company_id=self.company_id.id,
        )
        try:
            self.env.cr.execute(query_data)
            query_data = self.env.cr.dictfetchall()
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

        return query_data

    def _execute_lines_7_3_depreciation(self):
        def function_lines_7_3_dep_sql():
            lines_1.append({
                'id': self.exist_data(asset['id']),

                'period': self.date_start.strftime('%Y0000'),
                'cuo': self.clean_data(asset['am_name'])[:40],
                'correlative': self.clean_data(asset['correlative']),
                'asset_catalog_code': asset['asset_catalog_code'],
                'asset_code': self.exist_data(asset['asset_code']),

                'acquisition_date': asset['date'],
                'value_acquisition_exchange': "{:.2f}".format(0),
                'foreign_currency_exchange_rate': "{:.3f}".format(0),
                'value_acquisition_local': "{:.2f}".format(0),
                'currency_exchange_rate_3112': "{:.3f}".format(0),

                'adjust_difference_exchange_rate': "{:.2f}".format(0),
                'amount_withdrawals': "{:.2f}".format(asset['amount_total']) if asset['ple_selection'] == 'assets_book_acquisition_amortization' and amount_withdrawals == 0.00 else "{:.2f}".format(0),
                'dep_amount_withdrawals': "{:.2f}".format(dep_amount_withdrawals),
                'amount_other_ple': "{:.2f}".format(asset['amount_total']) if asset['ple_selection'] != 'assets_book_acquisition_amortization' else "{:.2f}".format(0),

            })
            return lines_1

        data_aseet = self.get_data_7_3_depreciation_sql()
        for asset in data_aseet:
            query = """
                SELECT am.name as name
                FROM account_asset as aa
                LEFT JOIN account_move am       ON  am.asset_id=aa.id
                WHERE aa.id = {asset_id} and aa.disposal_date is not null
                ORDER BY name desc
                LIMIT 1
            """.format(asset_id=asset['id'])
            try:
                self.env.cr.execute(query)
                query_data = self.env.cr.dictfetchall()
            except Exception as error:
                raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

            if len(query_data) != 0 and asset['am_name'] == query_data[0]['name'] and asset['disposal_date']:
                asset['special'] = True

        dep_amount_withdrawals = 0.00
        amount_withdrawals = 0.00
        lines_1 = []
        for asset in data_aseet:
            dep_amount_withdrawals = 0.00
            amount_withdrawals = 0.00
            for line in self.line31_query():
                if asset['move_id'] == line['id'] and asset.get('special', False):
                    dep_amount_withdrawals = line['amount']
                    amount_withdrawals = line['amount']
            function_lines_7_3_dep_sql()
        return lines_1

    def init_7_3(self):
        data_active = self._execute_lines_7_3_active()        
        data_active.extend(self._execute_lines_7_3_depreciation())
        data_active.sort(key=lambda x: x.get('id'))
        return data_active
