from ..reports.report_asset_book_7_3 import AssetsReport0703
from ..reports.report_assets import AssetsReport
from ..reports.report_assets_03 import AssetsReport03

from odoo import api, fields, models
from odoo.exceptions import ValidationError
import re
import base64

from datetime import datetime

MAX_NAME_LENGTH = 40


class PleAssetsBook(models.Model):
    _name = 'ple.report.assets.book'
    _description = 'Activos Fijos'
    _inherit = 'ple.report.base'

    xls_filename_assets_1 = fields.Char(string='Fileneme Excel - Revaluados y No revaluados')
    xls_binary_assets_1 = fields.Binary(string='Reporte Excel - Revaluados y No revaluados')
    txt_filename_assets_1 = fields.Char(string='Fileneme TXT - Revaluados y No revaluados')
    txt_binary_assets_1 = fields.Binary(string='Reporte TXT - Revaluados y No revaluados')

    xls_filename_assets_2 = fields.Char(string='Fileneme Excel - Diferencia de cambio')
    xls_binary_assets_2 = fields.Binary(string='Reporte Excel - Diferencia de cambio')
    txt_filename_assets_2 = fields.Char(string='Fileneme TXT - Diferencia de cambio')
    txt_binary_assets_2 = fields.Binary(string='Reporte TXT - Diferencia de cambio')

    xls_filename_assets_3 = fields.Char(string='Fileneme Excel - Arrendamiento Financiero')
    xls_binary_assets_3 = fields.Binary(string='Reporte Excel - Arrendamiento Financiero')
    txt_filename_assets_3 = fields.Char(string='Fileneme TXT - Arrendamiento Financiero')
    txt_binary_assets_3 = fields.Binary(string='Reporte TXT - Arrendamiento Financiero')

    def name_get(self):
        return [(obj.id, '{} - {}'.format(obj.date_start.strftime('%d/%m/%Y'), obj.date_end.strftime('%d/%m/%Y'))) for
                obj in self]

    def exist_data(self, parameter):
        return parameter if parameter else ''

    def _get_lines_1(self):
        QUERY_DATA = """
        CREATE OR REPLACE FUNCTION calculate_last_depreciation_move_ids(
                                            id_asset INTEGER,
                                            OUT move_id INTEGER) AS $$
        BEGIN
            SELECT 
            am.id  INTO move_id
            FROM account_move am
            WHERE am.asset_id=id_asset
            ORDER BY am.date DESC
            LIMIT 1;
        END;
        $$ 
        LANGUAGE plpgsql;

        CREATE OR REPLACE FUNCTION calculate_debitx_totalx(
                                            id_move_id INTEGER,
                                            OUT debit FLOAT) AS $$
        BEGIN
            SELECT sum(aml.debit) INTO debit
            FROM account_move am
            INNER JOIN account_move_line aml ON am.id=aml.move_id
            WHERE am.id=id_move_id;

        END;
        $$ 
        LANGUAGE plpgsql;

        CREATE OR REPLACE FUNCTION calculate_row_15 (date_start TIMESTAMP, 
                                            date_end TIMESTAMP , 
                                            asset_id INTEGER,
                                            OUT amount_pe FLOAT) AS $$
        BEGIN
            SELECT 
            aa.original_value INTO amount_pe
            FROM account_asset aa
            LEFT JOIN account_account  acc ON  acc.id=aa.account_asset_id
            LEFT JOIN account_group  ag    ON  acc.group_id=ag.id
            WHERE
            ag.code_prefix_start='33' and aa.id=asset_id;

        END;
        $$ 
        LANGUAGE plpgsql;


        CREATE OR REPLACE FUNCTION calculate_row_18(date_start TIMESTAMP, 
                                            date_end TIMESTAMP, 
                                            asset_account_id INT,
                                            OUT debit_total FLOAT) AS $$
        BEGIN
            SELECT calculate_debitx_totalx(am.id) into debit_total
            FROM 
            ACCOUNT_ASSET aa
            INNER JOIN ACCOUNT_MOVE am ON am.asset_id=aa.id
            INNER JOIN ACCOUNT_MOVE_LINE aml ON aml.move_id=am.id
            WHERE 
            aa.state='close' and
            am.id=calculate_last_depreciation_move_ids(asset_account_id)  and
            am.state='posted' and
            (date_start<=am.date)  and
            (am.date <= date_end) and
            aa.id=asset_account_id;            
        END;
        $$ 
        LANGUAGE plpgsql;

        
        CREATE OR REPLACE FUNCTION calculate_line_state_name(
                                                id_asset INTEGER,
                                                OUT move_id TEXT) AS $$
           BEGIN
              SELECT 
                AM. NAME INTO move_id
                FROM account_move am
                WHERE am.asset_id=id_asset
                ORDER BY am.date DESC
                LIMIT 1;
                END;
            $$ 
            LANGUAGE plpgsql;  
            
            CREATE OR REPLACE FUNCTION calculate_line_state_cuo(
                                                id_asset INTEGER,
                                                OUT move_id INTEGER) AS $$
           BEGIN
              SELECT 
                AM.ID INTO move_id
                FROM account_move am
                WHERE am.asset_id=id_asset
                ORDER BY am.date DESC
				LIMIT 1;
            END;
            $$ 
            LANGUAGE plpgsql;
         CREATE OR REPLACE FUNCTION num_correlative(date_start TIMESTAMP, 
                                               date_end TIMESTAMP, 
                                               asset_account_id INT,
                                               OUT name_col2 CHAR) AS $$
           BEGIN
             SELECT aml.ple_correlative into name_col2
               FROM 
               ACCOUNT_ASSET aa
               INNER JOIN ACCOUNT_MOVE am ON am.asset_id=aa.id
               INNER JOIN ACCOUNT_MOVE_LINE aml ON aml.move_id=am.id
               LEFT JOIN ACCOUNT_ACCOUNT acc ON  acc.id=aml.account_id
              LEFT JOIN ACCOUNT_GROUP  ag   ON  acc.group_id=ag.id
               WHERE 
               am.id=calculate_line_state_cuo(asset_account_id)  and
               am.state='posted' and   aa.id=asset_account_id and ag.code_prefix_start='33'
               limit 1;             
           END;
           $$ 
           LANGUAGE plpgsql;
    

        SELECT
        --line 1
        validate_string(COALESCE(am.name,aa.name),40) as name_cuo,
        aa.id as asset_id,
        ag.code_prefix_start as code_prefix_start,   
        COALESCE(aml.ple_correlative,'M000000001') as ple_correlative,
        aa.asset_catalog_code as catalog_code,
        COALESCE(aa.asset_code,'SC01') as asset_code,
        CASE WHEN aa.asset_cubso_osce!='' then '1' else '' end as asset_cb,
        aa.asset_cubso_osce as asset_cubso_osce,
        aa.fixed_asset_type as fixed_asset_type,
        validate_string(acc.code,8) as code_account_account,
        aa.fixed_asset_state as fixed_asset_state,
        SUBSTRING(aa.name from 1 for 40) as name_asset,
        COALESCE(SUBSTRING(aa.asset_brand from 1 for 40),'-') as asset_brand,
        COALESCE(SUBSTRING(aa.asset_model from 1 for 40),'-') as asset_model,
        COALESCE(SUBSTRING(aa.asset_series from 1 for 40),'-') as asset_series,
        calculate_row_15('{start_date}','{date_end}' ,aa.id) as calculate_row_15,
        COALESCE(calculate_row_18('{start_date}','{date_end}',aa.id),0.00) as calculate_row_18,
        TO_CHAR(aa.acquisition_date,'DD/MM/YYYY') as acquisition_date,
        TO_CHAR(aa.prorata_date, 'DD/MM/YYYY') as prorata_date,
        CASE WHEN aa.disposal_date is not null and aa.disposal_date >= '{start_date}' and aa.disposal_date <= '{date_end}' then True else False end as disposal_date,
        aa.prorata_date as date_condition_depreciation_date,
        aa.depreciation_method as depreciation_method,
        COALESCE(authorization_number_method_change,'SN') as authorization_number_method_change,
        aa.original_value as original_value,
        aa.parent_id as parent_id,
        aa.asset_rate as asset_rate,
        ag.code_prefix_start,
        acc.ple_selection as ple_selection,
        aa.state as state,
        date_part('year',now()) as today,
        --line state_close
        COALESCE(num_correlative('{start_date}','{date_end}',aa.id),'M000000001') as number_correlative_c_state,
        am.name as cuo_c_state
        FROM account_asset aa   --Table principal
        --JOINS Line 1
        LEFT JOIN asset_move_line_rel amlr  ON  amlr.asset_id=aa.id
        LEFT JOIN account_move_line aml     ON  amlr.line_id=aml.id
        LEFT JOIN account_move am           ON  aml.move_id=am.id
        LEFT JOIN account_account  acc      ON  acc.id=aa.account_asset_id
        LEFT JOIN account_group  ag         ON  acc.group_id=ag.id

        where
        --where line 1
       (aa.acquisition_date <= '{date_end}') and
        aa.company_id='{company_id}'  and  
        acc.ple_selection in ('assets_book_acquisition_asset','assets_book_improvements_asset',
        'assets_book_other_asset','assets_book_voluntary_revaluation_asset','assets_book_revaluation_reorganization_asset',
        'assets_book_revaluation_other_asset','assets_book_inflation_asset')

        """.format(
            start_date=self.date_start,
            date_end=self.date_end,
            company_id=self.company_id.id,
        )

        try:
            self.env.cr.execute(QUERY_DATA)
            query_data = self.env.cr.dictfetchall()
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

        return query_data

    def _execute_lines_1(self):
        query_data = self._get_lines_1()
        list_data = self._calculate_columns_AC_to_AD()        
        lines = []
        var_list = []
        list_parents = list(map(lambda r: r['parent_id'], query_data)) if query_data else []

        def function_lines():
            lines.append({
                'id': self.exist_data(asset['asset_id']),
                'code_prefix_start': self.exist_data(asset['code_prefix_start']),
                'period': self.date_start.strftime('%Y0000'),
                'cuo': self.exist_data(re.sub(r"[^a-zA-Z0-9]", "", asset['name_cuo'])[:40]),
                'correlative': self.exist_data(asset['ple_correlative']),
                'asset_catalog_code': self.exist_data(asset['catalog_code']),
                'asset_code': self.exist_data(asset['asset_code']),

                'used_catalog_code': self.exist_data(asset['asset_cb']),
                'unique_fixed_asset_type': self.exist_data(asset['asset_cubso_osce']),
                'fixed_asset_type': self.exist_data(asset['fixed_asset_type']),
                'account_code': self.exist_data(re.sub(r"[^a-zA-Z0-9]", "", asset['code_account_account'])),
                'fixed_asset_state': self.exist_data(asset['fixed_asset_state']),
                'description': self.exist_data(asset['name_asset']),

                'asset_brand': asset['asset_brand'] if asset['asset_brand'] else '-',
                'asset_model': asset['asset_model'] if asset['asset_model'] else '-',
                'asset_series': asset['asset_series'] if asset['asset_series'] else '-',
                'asset_opening': calculate_14 if calculate_14 else 0.00,
                'asset_amount': 0.00 if asset['parent_id'] else calculate_15 if asset['ple_selection'] == 'assets_book_acquisition_asset' else 0.00,
                'amount_improvement': 0.00 if asset['parent_id'] else calculate_15 if asset['ple_selection'] == 'assets_book_improvements_asset' else 0.00,
                'amount_withdrawals': -calculate_16 if calculate_16 > 0.00 else 0.00,
                'amount_other_adjustments': 0.00 if asset['parent_id'] else calculate_15 if asset['ple_selection'] == 'assets_book_other_asset' else 0.00,
                'amount_voluntary_revaluation': 0.00 if asset['parent_id'] else calculate_15 if asset['ple_selection'] == 'assets_book_voluntary_revaluation_asset' else 0.00,
                'amount_revaluation_reorganization': 0.00 if asset['parent_id'] else calculate_15 if asset['ple_selection'] == 'assets_book_revaluation_reorganization_asset' else 0.00,

                'amount_other_revaluation': 0.00 if asset['parent_id'] else calculate_15 if asset['ple_selection'] == 'assets_book_revaluation_other_asset' else 0.00,
                'amount_inflation_adjustment': 0.00 if asset['parent_id'] else calculate_15 if asset['ple_selection'] == 'assets_book_inflation_asset' else 0.00,

                'acquisition_date': asset['acquisition_date'],
                'start_date': asset['prorata_date'],
                'code_calculation_depreciation': asset['depreciation_method'],

                'authorization_document_number': asset['authorization_number_method_change'],
                'depreciation_percentage': asset['asset_rate'] if asset['asset_rate'] else 0.00,
                'accumulated_depreciation_end_previous_year': -calculate_29 if calculate_29 else 0.00,
                'amount_depreciation_without_revaluation': 0.00,
                'amount_depreciation_withdrawals': 0.00,

                'amount_depreciation_other_adjustments': 0.00,
                'amount_depreciation_voluntary_revaluation': 0.00,
                'amount_depreciation_revaluation_reorganization': 0.00,
                'amount_depreciation_revaluations': 0.00,
                'amount_depreciation_inflation': 0.00,
                'state': asset['state'],
            })
            return lines

        for asset in query_data:
            for var_list in list_data:
                if asset['asset_id'] == var_list['id']:
                    calculate_14 = round(var_list['data'][4],2)
                    calculate_15  = round(var_list['data'][5],2)
                    calculate_16  = round(var_list['data'][6],2)
                    calculate_29  = round(var_list['data'][8],2)
                    if asset['state'] == 'open':
                        function_lines()
                        if asset['asset_id'] in list_parents:
                            values_update_parents_active = ({'asset_amount': 0.00, })
                            lines[-1].update(values_update_parents_active)

                        if self.date_end.year > datetime.now().year:

                            if lines[-1]['asset_opening'] > 0.0:
                                values_update_parents_active_down = ({
                                    'amount_improvement': 0.00,
                                    'amount_withdrawals': 0.00,
                                    'amount_other_adjustments': 0.00,
                                    'amount_voluntary_revaluation': 0.00,
                                    'amount_revaluation_reorganization': 0.00,
                                    'amount_other_revaluation': 0.00,
                                    'amount_inflation_adjustment': 0.00,
                                    'amount_depreciation_withdrawals': 0.00,
                                    'amount_depreciation_other_adjustments': 0.00,
                                    'amount_depreciation_voluntary_revaluation': 0.00,
                                    'amount_depreciation_revaluation_reorganization': 0.00,
                                    'amount_depreciation_revaluations': 0.00,
                                    'amount_depreciation_inflation': 0.00,
                                })
                                lines[-1].update(values_update_parents_active_down)
                            else:
                                del lines[-1]

                    if asset['state'] == 'close':
                        function_lines()
                        values_update_close_line_1 = ({'amount_withdrawals': 0.00, })
                        lines[-1].update(values_update_close_line_1)
                        if asset['disposal_date']:
                            
                            query = """
                                SELECT 
                                    COALESCE(correlative_dep(aa.id,am.id),'M000000001') as correlative,
                                    am.name as name
                                FROM account_asset as aa
                                LEFT JOIN account_move am       ON  am.asset_id=aa.id
                                WHERE aa.id = {asset_id}
                                ORDER BY name desc
                                LIMIT 1
                            """.format(asset_id=asset['asset_id'])
                            try:
                                self.env.cr.execute(query)
                                query_data = self.env.cr.dictfetchall()
                            except Exception as error:
                                raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')
                                
                            function_lines()

                            if len(query_data) != 0:
                                lines[-1].update({
                                    'cuo': self.clean_data(query_data[0]['name'])[:40],
                                    'correlative': self.clean_data(query_data[0]['correlative']),
                                })

                            lines[-1].update({
                                'asset_opening': 0.00,
                                'accumulated_depreciation_end_previous_year':  0.00,
                                'asset_amount': 0.00
                            })
            if asset['parent_id']:
                function_lines()
                values_update_parent = ({
                    'asset_opening': 0.00,
                    'asset_amount': asset['original_value'] if asset['ple_selection'] == 'assets_book_acquisition_asset' else 0.00,
                    'amount_improvement': asset['original_value'] if asset['ple_selection'] == 'assets_book_improvements_asset' else 0.00,
                    'amount_withdrawals': -asset['calculate_row_18'] if asset['calculate_row_18'] else 0.00,
                    'amount_other_adjustments': asset['original_value'] if asset['ple_selection'] == 'assets_book_other_asset' else 0.00,
                    'amount_voluntary_revaluation': asset['original_value'] if asset['ple_selection'] == 'assets_book_voluntary_revaluation_asset' else 0.00,
                    'amount_revaluation_reorganization': asset['original_value'] if asset['ple_selection'] == 'assets_book_revaluation_reorganization_asset' else 0.00,
                    'amount_other_revaluation': asset['original_value'] if asset['ple_selection'] == 'assets_book_revaluation_other_asset' else 0.00,
                    'amount_inflation_adjustment': asset['original_value'] if asset['ple_selection'] == 'assets_book_inflation_asset' else 0.00,
                    'accumulated_depreciation_end_previous_year': 0.00,
                })
                lines[-1].update(values_update_parent)
                if self.date_end.year > datetime.now().year:
                    if lines[-1]['asset_opening'] > 0.0:
                        values_update_parents_active_down = ({'amount_improvement': 0.00,
                                                          'amount_withdrawals': 0.00,
                                                          'amount_other_adjustments': 0.00,
                                                          'amount_voluntary_revaluation': 0.00,
                                                          'amount_revaluation_reorganization': 0.00,
                                                          'amount_other_revaluation': 0.00,
                                                          'amount_inflation_adjustment': 0.00,
                                                          'amount_depreciation_withdrawals': 0.00,
                                                          'amount_depreciation_other_adjustments': 0.00,
                                                          'amount_depreciation_voluntary_revaluation': 0.00,
                                                          'amount_depreciation_revaluation_reorganization': 0.00,
                                                          'amount_depreciation_revaluations': 0.00,
                                                          'amount_depreciation_inflation': 0.00,
                                                          })
                        lines[-1].update(values_update_parents_active_down)
                    else:
                        del lines[-1]

        return lines

    def line31_query(self):
        query = """
               SELECT 
                 aml.balance as amount, 
                 am.id  as id
               FROM 
                 account_move am 
                 INNER JOIN account_move_line aml ON am.id = aml.move_id 
                 INNER JOIN account_account acc ON acc.id = aml.account_id 
                 INNER JOIN account_group ag ON acc.group_id = ag.id 
                 INNER JOIN account_asset aa ON am.asset_id = aa.id 
               WHERE 
                 aa.state = 'close' 
                 and am.state = 'posted' 
                 and ('{}' <= am.date) 
                 and (am.date <='{}') 
                 and ag.code_prefix_start = '39'
               """.format(self.date_start, self.date_end)
        try:
            self.env.cr.execute(query)
            data = self.env.cr.dictfetchall()
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')
        return data

    def _get_lines_2(self):
        QUERY_DATA = """
        CREATE OR REPLACE FUNCTION calculate_first_depreciation_move_ids(
                                                id_asset INTEGER,
                                                OUT move_id INTEGER) AS $$
            BEGIN
                SELECT 
                am.id  INTO move_id
                FROM account_move am
                WHERE am.asset_id=id_asset
                ORDER BY am.date asc 
                LIMIT 1;
            END;
            $$ 
            LANGUAGE plpgsql;

           
       CREATE OR REPLACE FUNCTION correlative_dep(aa_id INT, am_id INT,
                                                   OUT nameX CHAR) AS $$
               BEGIN
                   SELECT aml.ple_correlative INTO nameX
                   FROM 
                   ACCOUNT_ASSET aa
                   LEFT JOIN ACCOUNT_MOVE am ON am.asset_id=aa.id
                   LEFT JOIN ACCOUNT_MOVE_LINE aml ON aml.move_id=am.id
                   LEFT JOIN ACCOUNT_ACCOUNT acc ON  acc.id=aml.account_id
                 LEFT JOIN ACCOUNT_GROUP  ag   ON  acc.group_id=ag.id
                   WHERE 
                   am.state='posted' and aa.id=aa_id and am.id=am_id and ag.code_prefix_start='39';
                          
               END;
               $$ 
               LANGUAGE plpgsql;


    CREATE OR REPLACE FUNCTION calculate_col_31(date_start TIMESTAMP, 
                                            date_end TIMESTAMP, 
                                            asset_account_id INT,
                                            OUT debit_total FLOAT) AS $$
        BEGIN
            SELECT sum(aml.debit) into debit_total

            FROM 
            ACCOUNT_ASSET aa
            INNER JOIN account_account  acc  ON  acc.id=aa.account_depreciation_id
            INNER JOIN account_group  ag     ON  acc.group_id=ag.id
            INNER JOIN ACCOUNT_MOVE am       ON   am.asset_id=aa.id
            INNER JOIN account_move_line aml ON am.id=aml.move_id
            WHERE 
            aa.state='close' and
            am.state='posted' and
            (date_start<=am.date)  and
            (am.date <= date_end) and
            acc.ple_selection='assets_book_acquisition_amortization' and
            aa.id=asset_account_id and 
            am.id=(SELECT ac_mo.id FROM account_move ac_mo WHERE ac_mo.asset_id=aa.id  ORDER BY ac_mo.date ASC LIMIT 1);

        END;
        $$ 
        LANGUAGE plpgsql;    
        
        
        CREATE OR REPLACE FUNCTION calculate_increase_DEP_amount(date_start TIMESTAMP, 
                                            date_end TIMESTAMP,
                                            asset_id INTEGER,
                                            ple_code TEXT,
                                            OUT amount_pe FLOAT) AS $$
        BEGIN
            SELECT aa.original_value INTO amount_pe
            FROM account_asset aa
            LEFT JOIN account_account  acc ON  acc.id=aa.account_depreciation_id
            LEFT JOIN account_group  ag    ON  acc.group_id=ag.id
            WHERE 
			aa.id in (select ax.id from account_asset ax WHERE ax.parent_id=asset_id) AND 
            acc.ple_selection= ple_code AND
            (date_start<=aa.acquisition_date)  and  (aa.acquisition_date <=date_end) and
            ag.code_prefix_start='39';

        END;
        $$ 
        LANGUAGE plpgsql;
       CREATE OR REPLACE FUNCTION amount_total_currency(date_start TIMESTAMP, 
                                               date_end TIMESTAMP, 
                                               asset_account_id INT,
												acc_move_id INT,
                                               OUT currency_amount FLOAT) AS $$
           BEGIN
             SELECT aml.balance into currency_amount
               FROM 
               ACCOUNT_ASSET aa
               LEFT JOIN ACCOUNT_MOVE am 		ON 	am.asset_id=aa.id
               LEFT JOIN ACCOUNT_MOVE_LINE aml ON  aml.move_id=am.id
               LEFT JOIN ACCOUNT_ACCOUNT acc 	ON  acc.id=aml.account_id
              LEFT JOIN ACCOUNT_GROUP  ag  		ON  acc.group_id=ag.id
               WHERE 
			    am.id=acc_move_id  and
               am.state='posted' and   aa.id=asset_account_id and ag.code_prefix_start='39'
               limit 1;             
           END;
           $$ 
           LANGUAGE plpgsql;


        SELECT
           aa.id as id,
           ag.code_prefix_start as code_prefix_start,
          correlative_dep(aa.id,am.id) as correlative,
           aa.asset_catalog_code as  asset_catalog_code,
           COALESCE(aa.asset_code,'SC01') as asset_code,

           CASE WHEN aa.asset_cubso_osce!='' then '1' else '' end as asset_cb,
           aa.asset_cubso_osce as asset_cubso_osce,
           aa.fixed_asset_type as fixed_asset_type,
           validate_string(acc.code,8) as code_account_account,
           aa.fixed_asset_state as fixed_asset_state,

           SUBSTRING(aa.name from 1 for 40) as name_asset,
           COALESCE(SUBSTRING(aa.asset_brand from 1 for 40),'-') as asset_brand,
           COALESCE(SUBSTRING(aa.asset_model from 1 for 40),'-') as asset_model,
           COALESCE(SUBSTRING(aa.asset_series from 1 for 40),'-') as asset_series,

           TO_CHAR(aa.acquisition_date,'DD/MM/YYYY') as acquisition_date,
           aa.acquisition_date as _acquisition_date,
           TO_CHAR(aa.prorata_date, 'DD/MM/YYYY') as prorata_date,
           aa.prorata_date as date_condition_depreciation_date,
           aa.depreciation_method as depreciation_method,
           COALESCE(authorization_number_method_change,'SN') as authorization_number_method_change,
           aa.asset_rate as asset_rate,
           aa.parent_id as parent_id,
           am.date as am_date,
           am.name as am_name,
           am.asset_remaining_value as asset_remaining_value,
           amount_total_currency('{start_date}','{date_end}',aa.id,am.id) as am_amount_total,
           ag.code_prefix_start,
           am.id as account_move_id,
           aa.state as state,
           acc.ple_selection as ple_selection,
           date_part('year',now()) as today,
           calculate_col_31('{start_date}','{date_end}',aa.id)  as calculate_col31_1,
           calculate_increase_DEP_amount('{start_date}','{date_end}',aa.id,'assets_book_acquisition_amortization') as calculate_col31,
           calculate_increase_DEP_amount('{start_date}','{date_end}',aa.id,'assets_book_other_amortization') as calculate_col32,
           calculate_increase_DEP_amount('{start_date}','{date_end}',aa.id,'assets_book_voluntary_revaluation_amortization') as calculate_col33,
           calculate_increase_DEP_amount('{start_date}','{date_end}',aa.id,'assets_book_revaluation_reorganization_amortization') as calculate_col34,
           calculate_increase_DEP_amount('{start_date}','{date_end}',aa.id,'assets_book_revaluation_other_amortization') as calculate_col35,
           calculate_increase_DEP_amount('{start_date}','{date_end}',aa.id,'assets_book_inflation_amortization') as calculate_col36


           FROM ACCOUNT_ASSET aa
           LEFT JOIN ACCOUNT_MOVE am       ON  am.asset_id=aa.id
           LEFT JOIN ACCOUNT_ACCOUNT acc    ON  acc.id=aa.account_depreciation_id
           LEFT JOIN ACCOUNT_GROUP  ag      ON  acc.group_id=ag.id  
            
            WHERE
            ('{start_date}'<=am.date and am.date <= '{date_end}') and
            aa.company_id={company_id} and ag.code_prefix_start ='39' and  am.state='posted' and
            acc.ple_selection in ('assets_book_acquisition_amortization',
            'assets_book_other_amortization','assets_book_voluntary_revaluation_amortization',
            'assets_book_revaluation_reorganization_amortization', 'assets_book_revaluation_other_amortization',
            'assets_book_inflation_amortization')
            """.format(
            start_date=self.date_start,
            date_end=self.date_end,
            company_id=self.company_id.id,
        )

        try:
            self.env.cr.execute(QUERY_DATA)
            query_data = self.env.cr.dictfetchall()
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')
        lines = []
        line_del = self.del_depreciation_lines()
        ld = []
        for i in line_del:
            ld += i.values()
        list_parents = []
        for r in query_data:
            list_parents.append(r['parent_id'])


        def function_lines_2():
            alternative = None if asset['state'] == 'close' else 0.00
            lines.append({
                'id': asset['id'],
                'code_prefix_start': asset['code_prefix_start'] if asset['code_prefix_start'] else '',
                'period': self.date_end.strftime('%Y0000'),
                'cuo': re.sub(r"[^a-zA-Z0-9]", "", asset['am_name']) if asset['am_name'] else '',
                'correlative': asset['correlative'] if asset['correlative'] else '',
                'asset_catalog_code': asset['asset_catalog_code'] if asset['asset_catalog_code'] else '',
                'asset_code': asset['asset_code'] if asset['asset_code'] else '',

                'used_catalog_code': asset['asset_cb'] if asset['asset_cb'] else '',
                'unique_fixed_asset_type': asset['asset_cubso_osce'] if asset['asset_cubso_osce'] else '',
                'fixed_asset_type': asset['fixed_asset_type'] if asset['fixed_asset_type'] else '',
                'account_code': re.sub(r"[^a-zA-Z0-9]", "", asset['code_account_account']) if asset[
                    'code_account_account'] else '',
                'fixed_asset_state': asset['fixed_asset_state'] if asset['fixed_asset_state'] else '',
                'description': asset['name_asset'] if asset['name_asset'] else '',

                'asset_brand': asset['asset_brand'] if asset['asset_brand'] else '-',
                'asset_model': asset['asset_model'] if asset['asset_model'] else '-',
                'asset_series': asset['asset_series'] if asset['asset_series'] else '-',
                'asset_opening': "0.00",

                'asset_amount': 0.00,
                'amount_improvement': 0.00,
                'amount_withdrawals': 0.00,
                'amount_other_adjustments': 0.00,
                'amount_voluntary_revaluation': 0.00,
                'amount_revaluation_reorganization': 0.00,

                'amount_other_revaluation': 0.00,
                'amount_inflation_adjustment': 0.00,
                'acquisition_date': asset['acquisition_date'],
                'start_date': asset['prorata_date'],
                'code_calculation_depreciation': asset['depreciation_method'],

                'authorization_document_number': asset['authorization_number_method_change'],
                'depreciation_percentage': asset['asset_rate'] if asset['asset_rate'] else 0.00,
                'accumulated_depreciation_end_previous_year': 0.00,
                'amount_depreciation_without_revaluation': asset['am_amount_total'] if asset['ple_selection'] == 'assets_book_acquisition_amortization' else alternative,

                'amount_depreciation_withdrawals': asset['calculate_col31_1'] if asset['calculate_col31_1'] else alternative,
                'amount_depreciation_other_adjustments': asset['am_amount_total'] if asset['ple_selection'] == 'assets_book_other_amortization' else alternative,
                'amount_depreciation_voluntary_revaluation': asset['am_amount_total'] if asset['ple_selection'] == 'assets_book_voluntary_revaluation_amortization' else alternative,
                'amount_depreciation_revaluation_reorganization': asset['am_amount_total'] if asset['ple_selection'] == 'assets_book_revaluation_reorganization_amortization' else alternative,
                'amount_depreciation_revaluations': asset['am_amount_total'] if asset['ple_selection'] == 'assets_book_revaluation_other_amortization' else alternative,
                'amount_depreciation_inflation': asset['am_amount_total'] if asset['ple_selection'] == 'assets_book_inflation_amortization'  else alternative,
                'state': asset['state'],
                'account_move_id': asset['account_move_id'],

            })

            return lines

        data_update = self.line31_query()
        for asset in query_data:
            if asset['account_move_id'] not in ld:
                function_lines_2()
                if asset['state'] == 'open' and asset['id'] in list_parents and not asset['parent_id']:
                    value_update = ({
                        'amount_depreciation_without_revaluation': asset['am_amount_total'],
                        'amount_depreciation_withdrawals': 0.00,
                        'amount_depreciation_other_adjustments': 0.00,
                        'amount_depreciation_voluntary_revaluation': 0.00,
                        'amount_depreciation_revaluation_reorganization': 0.00,
                        'amount_depreciation_revaluations': 0.00,
                        'amount_depreciation_inflation': 0.00,
                    })
                    lines[-1].update(value_update)
                elif asset['state'] == 'open' and asset['parent_id']:
                    value_update = ({
                        'amount_depreciation_without_revaluation': 0.00,
                        'amount_depreciation_withdrawals': 0.00,
                        'amount_depreciation_other_adjustments': asset['am_amount_total'] if asset['ple_selection'] == 'assets_book_other_amortization' else 0.00,
                        'amount_depreciation_voluntary_revaluation': asset['am_amount_total'] if asset['ple_selection'] == 'assets_book_voluntary_revaluation_amortization' else 0.00,
                        'amount_depreciation_revaluation_reorganization': asset['am_amount_total'] if asset['ple_selection'] == 'assets_book_revaluation_reorganization_amortization' else 0.00,
                        'amount_depreciation_revaluations': asset['am_amount_total'] if asset['ple_selection'] == 'assets_book_revaluation_other_amortization' else 0.00,
                        'amount_depreciation_inflation': asset['am_amount_total'] if asset['ple_selection'] == 'assets_book_inflation_amortization' else 0.00,
                    })
                    lines[-1].update(value_update)
                elif asset['state'] == 'close':
                    for line_update in data_update:
                        if asset['account_move_id'] == line_update['id']:
                            value_update = ({
                                'amount_depreciation_without_revaluation': line_update['amount'] if asset['asset_remaining_value'] != 0 else 0.00,
                                'amount_depreciation_withdrawals': 0.00 if asset['asset_remaining_value'] != 0 else line_update['amount'],
                                'amount_depreciation_other_adjustments': line_update['amount'] if asset['ple_selection']=='assets_book_other_amortization' and
                                                                                                  asset['asset_remaining_value'] == 0 else 0.00,
                                'amount_depreciation_voluntary_revaluation': line_update['amount'] if asset['ple_selection']=='assets_book_voluntary_revaluation_amortization' and
                                                                                                      asset['asset_remaining_value'] == 0 else 0.00,
                                'amount_depreciation_revaluation_reorganization': line_update['amount'] if asset['ple_selection']=='assets_book_revaluation_reorganization_amortization' and
                                                                                                           asset['asset_remaining_value'] == 0 else 0.00,
                                'amount_depreciation_revaluations': line_update['amount'] if asset['ple_selection']=='assets_book_revaluation_other_amortization' and
                                                                                             asset['asset_remaining_value'] == 0 else 0.00,
                                'amount_depreciation_inflation': line_update['amount'] if asset['ple_selection']=='assets_book_inflation_amortization' and
                                                                                          asset['asset_remaining_value'] == 0 else 0.00,
                            })
                            lines[-1].update(value_update)
                else:
                    pass

        return lines

    def del_depreciation_lines(self):
        query = """ SELECT DISTINCT AX.REVERSED_ENTRY_ID FROM ACCOUNT_MOVE AX"""
        self.env.cr.execute(query)
        query_data = self.env.cr.dictfetchall()
        return query_data

    def _calculate_columns_AC_to_AD(self):
        options = { 'unfolded_lines': [],
                    'report_id':18,
                    'allow_domestic': False,
                    'fiscal_position': 'all',
                    'available_vat_fiscal_positions': [], 
                    'date': {'string': self.date_start.year,
                             'period_type': 'fiscalyear', 
                             'mode': 'range',
                             'strict_range': False, 
                             'date_from': self.date_start,
                             'date_to': self.date_end, 'filter': 'custom'},
                    'all_entries': False,
                    'hierarchy': False, 
                    'unfold_all': False, 
                    'unposted_in_period': True}

        report_options = self.env.ref('account_asset.assets_report')._get_options(previous_options=options)        
        result_native = self.env.ref('account_asset.assets_report')._get_lines(report_options)
        lista = []

        for dict in result_native:
            id_asset = dict['id'].split("|~account.asset~")
            if len(id_asset)>1: 
                lista.append({
                    'id':int(id_asset[1]),
                    'data':list(map(lambda column: column['no_format'], dict['columns']))
                })
        
        if len(lista) > 0:
            for dict in lista:
                asset_id = self.env['account.asset'].browse(dict['id'])
                if asset_id and asset_id.currency_id != self.company_id.currency_id:
                    for position, column in enumerate(dict['data']):
                        if isinstance(column, (int, float)):
                            inverse_exchange_rate = self._get_inverse_exchange_rate(
                                asset_id.currency_id, 
                                asset_id.acquisition_date or fields.Date.context_today(self)
                            )
                            new_value = column / inverse_exchange_rate
                            new_value_round = self.company_id.currency_id.round(new_value)
                            dict['data'][position] = new_value_round
        return lista

    def _get_inverse_exchange_rate(self, currency, acquisition_date):
        return self.env['res.currency']._get_conversion_rate(
            from_currency=self.company_id.currency_id or self.env.company.currency_id,
            to_currency=currency,
            company=self.company_id,
            date=acquisition_date,
        )

    def action_generate_excel(self):
        asset_data_1 = self._execute_lines_1()
        asset_data_2 = self._get_lines_2()
        asset_data_1.extend(asset_data_2)
        asset_data_1.sort(key=lambda x: x.get('id')),


        report_1 = AssetsReport(self, asset_data_1)
        asset_content_txt_1 = report_1.get_content_txt()
        asset_content_xls_1 = report_1.get_content_excel()

        report_3 = AssetsReport03(self, self.get_data_report_03())
        asset_content_txt_3 = report_3.get_content_txt()
        asset_content_xls_3 = report_3.get_content_excel()

        report_2 = AssetsReport0703(self, self.init_7_3())
        asset_content_xls_2 = report_2.get_content_excel()
        asset_content_txt_2 = report_2.get_content_txt()
        error_dialog = ''

        if not asset_content_txt_1:
            error_dialog += '- No hay contenido en el registro "Detalle de los activos fijos - Revaluados y No revaluados.\n'
        data = {
            'txt_binary_assets_1': base64.b64encode(
                asset_content_txt_1 and asset_content_txt_1.encode() or '\n'.encode()),
            'txt_filename_assets_1': report_1.get_filename(file_type='txt', book_identifier='070100'),
            'xls_binary_assets_1': base64.b64encode(asset_content_xls_1),
            'xls_filename_assets_1': report_1.get_filename(file_type='xlsx', book_identifier='070100'),

            'txt_binary_assets_2': base64.b64encode(
                asset_content_txt_2 and asset_content_txt_2.encode() or '\n'.encode()),
            'txt_filename_assets_2': report_2.get_filename(file_type='txt', book_identifier='070300'),
            'xls_binary_assets_2': base64.b64encode(asset_content_xls_2),
            'xls_filename_assets_2': report_2.get_filename(file_type='xlsx', book_identifier='070300'),

            'txt_binary_assets_3': base64.b64encode(
                asset_content_txt_3 and asset_content_txt_3.encode() or '\n'.encode()),
            'txt_filename_assets_3': report_3.get_filename(file_type='txt', book_identifier='070400'),
            'xls_binary_assets_3': base64.b64encode(asset_content_xls_3),
            'xls_filename_assets_3': report_3.get_filename(file_type='xlsx', book_identifier='070400'),

            'error_dialog': error_dialog,
            'date_ple': fields.Date.today(),
            'state': 'load'
        }
        self.write(data)

    def action_close(self):
        self.ensure_one()
        self.write({
            'state': 'closed'
        })

    def action_rollback(self):
        self.state = 'draft'
        self.write({
            'xls_binary_assets_1': False,
            'xls_binary_assets_2': False,
            'xls_binary_assets_3': False,
            'txt_binary_assets_1': False,
            'txt_binary_assets_2': False,
            'txt_binary_assets_3': False,
        })
