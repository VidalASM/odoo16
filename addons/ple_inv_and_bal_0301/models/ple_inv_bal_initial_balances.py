from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class PleInvBalInitial(models.Model):
    _inherit = 'ple.report.inv.bal'

    line_initial_ids = fields.One2many(
        comodel_name='ple.inv.bal.line.initial.balances',
        inverse_name='ple_report_inv_val_id',
        string='Líneas'
    )


    def action_generate_initial_balances(self):
        self.line_initial_ids.unlink()
        account_query = """
                SELECT account_account.id
                 -- QUERIES TO MATCH MULTI TABLES
                    FROM eeff_ple
                --  TYPE JOIN   |  TABLE                        | MATCH
                    INNER JOIN   account_account                ON account_account.eeff_ple_id = eeff_ple.id
                -- FILTER QUERIES 
                    WHERE eeff_ple.eeff_type = '3.1';                    
        """
        self.env.cr.execute(account_query)
        val_account = self.env.cr.dictfetchall()

        if not val_account:
            self.write({'error_dialog': 'No hay cuentas configuradas con tipo 3.1 ESF'})
            return True

        acc_q = []
        for i in val_account:
            acc_q.append(i['id'])

        query = """
        SELECT
                eeff_ple.sequence as sequence,
                '{date_self}' as name,
                '{financial_statements_catalog}' as catalog_code,
                eeff_ple.code as financial_state_code,
                eeff_ple.id as eeff_ple_id,
                eeff_ple.id as parent,
                eeff_ple.description as description,
                UDF_numeric_char(sum(account_move_line.balance)) as credit,
                {ple_report_inv_val_id} as ple_report_inv_val_id
            -- QUERIES TO MATCH MULTI TABLES
                FROM account_move_line 
            --  TYPE JOIN   |  TABLE                        | MATCH
                INNER JOIN    account_account               ON account_move_line.account_id = account_account.id
                INNER JOIN    eeff_ple                      ON eeff_ple.id = account_account.eeff_ple_id
            -- FILTER QUERIES 
                WHERE eeff_ple.eeff_type = '3.1' and 
                account_move_line.date <= '{date_end}' and ((account_move_line.date >= '{date_start}') OR 
                "account_move_line"."account_id" in( SELECT "account_account".id FROM "account_account"
                 WHERE ("account_account"."include_initial_balance" = True)))
                and account_move_line.company_id = {company_id} and  ("account_move_line"."account_id" in {accounts})
                and account_move_line.parent_state = '{state}'
                GROUP BY
                    eeff_ple.sequence, eeff_ple.code, eeff_ple.id, eeff_ple, parent;
        """.format(
            company_id=self.company_id.id,
            date_start=self.date_start,
            date_end=self.date_end - relativedelta(years=1),
            state='posted',
            financial_statements_catalog=self.financial_statements_catalog,
            date_self=self.date_end.strftime('%Y%m%d'),
            accounts=tuple(acc_q),
            ple_report_inv_val_id=self.id
        )

        try:
            self.env.cr.execute(query)
            values = self.env.cr.dictfetchall()

            for dict in values:
                dict.setdefault('state', '1')

            lines_data = {}
            for dict in values:
                self.check_key_in_dicts(dict['eeff_ple_id'], lines_data, dict)
                self.check_parent_lines(dict['parent'], dict['credit'], lines_data)

            lines_report = list(lines_data.values())
            for data in lines_report:
                if len(data) == 10:
                    del data['parent']
            self.env['ple.inv.bal.line.initial.balances'].create(lines_report)

        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

    def action_generate_initial_balances_301(self):
        return self.action_generate_initial_balances()



class PleInvBalLinesInitial(models.Model):
    _name = 'ple.inv.bal.line.initial.balances'
    _description = 'Estado de Situación financiera de saldos iniciales - Líneas'
    _order = 'sequence desc'

    sequence = fields.Integer(string='Secuencia')
    ple_report_inv_val_id = fields.Many2one(
        comodel_name='ple.report.inv.bal',
        string='Reporte de Estado de Situación financiera'
    )
    name = fields.Char(string='Periodo')
    catalog_code = fields.Char(string='Código de catálogo')
    financial_state_code = fields.Char(string='Código del Rubro del Estado Financiero')
    eeff_ple_id = fields.Many2one(
        string='Rubro EEFF PLE',
        comodel_name='eeff.ple'
    )
    credit = fields.Char(string='Saldo del Rubro Contable')
    state = fields.Char(string='Indica el estado de la operación')
    account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Cuentas',
        readonly=1
    )
    description = fields.Char(
        string='Descripción'
    )
    code_eeff = fields.Char(string='Código del rubro del EEFF', compute='calculate_name_code')
    nombre_eeff = fields.Char(string='Nombre del rubro del EEFF', compute='calculate_name_code')

    def calculate_name_code(self):
        for rec in self:
            data = rec.eeff_ple_id
            rec.code_eeff = data.code
            rec.nombre_eeff = data.description


