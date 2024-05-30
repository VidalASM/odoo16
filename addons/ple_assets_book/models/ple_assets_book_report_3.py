from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    contract_number = fields.Char(string="Nro. del contrato de arrendamiento Financiero")


class PleAssetsBook(models.Model):
    _inherit = 'ple.report.assets.book'

    def get_data_report_03(self):
        query_data_1 = """
            SELECT 
                validate_string(translate(COALESCE(am.name, aa.name), ' ', ''), 40) as cuo,
                COALESCE(aml.ple_correlative, 'M000000001') as ple_correlative,
                aa.asset_catalog_code as asset_catalog_code,
                validate_string(COALESCE(aa.contract_number, ''), 20) as contract_number,
                TO_CHAR(aa.acquisition_date,'DD/MM/YYYY') as acquisition_date,
                COALESCE(aa.asset_code,'SC01') as asset_code,
                TO_CHAR(COALESCE(aa.first_depreciation_date_import, COALESCE(aa.prorata_date, aa.acquisition_date)), 'DD/MM/YYYY') as asset_date_init,
                aa.method_number as method_number,
                aa.original_value as original_value,
                 aa.id as id
            FROM account_asset aa
                JOIN asset_move_line_rel amlr  ON  amlr.asset_id=aa.id
                LEFT JOIN account_move_line aml     ON  amlr.line_id=aml.id
                LEFT JOIN account_move am           ON  aml.move_id=am.id
                LEFT JOIN account_account  acc      ON  acc.id=aa.account_asset_id
                LEFT JOIN account_group  ag         ON  acc.group_id=ag.id
            WHERE
                aa.acquisition_date <= '{date_end}' AND
                aa.company_id='{company_id}'  AND
                contract_number IS NOT NULL AND
                aa.state != 'draft'
        """.format(
            date_start=self.date_start,
            date_end=self.date_end,
            company_id=self.company_id.id,
        )


        query_data_2 = """
            SELECT 
                validate_string(translate(COALESCE(aa.name), ' ', ''), 40) as cuo,
                COALESCE('M000000001') as ple_correlative,
                aa.asset_catalog_code as asset_catalog_code,
                validate_string(COALESCE(aa.contract_number, ''), 20) as contract_number,
                TO_CHAR(aa.acquisition_date,'DD/MM/YYYY') as acquisition_date,
                COALESCE(aa.asset_code,'SC01') as asset_code,
                TO_CHAR(COALESCE(aa.first_depreciation_date_import, COALESCE(aa.prorata_date, aa.acquisition_date)), 'DD/MM/YYYY') as asset_date_init,
                aa.method_number as method_number,
                aa.original_value as original_value,
                aa.id as id
                
            FROM account_asset aa
                LEFT JOIN account_account  acc      ON  acc.id=aa.account_asset_id
                LEFT JOIN account_group  ag         ON  acc.group_id=ag.id
            WHERE
                aa.acquisition_date <= '{date_end}' AND
                aa.company_id='{company_id}'  AND
                contract_number IS NOT NULL AND
                aa.state != 'draft'
                """.format(
            date_start=self.date_start,
            date_end=self.date_end,
            company_id=self.company_id.id,
        )

        try:
            data_1 , data_2 = [],[]
            self.env.cr.execute(query_data_1)
            data_1 = self.env.cr.dictfetchall()

            self.env.cr.execute(query_data_2)
            data_2 = self.env.cr.dictfetchall()
            filtro = lambda elem: elem['id'] not in [e['id'] for e in data_1]
            data_filter = list(filter(filtro, data_2))
            data = data_1+data_filter

        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

        return data
