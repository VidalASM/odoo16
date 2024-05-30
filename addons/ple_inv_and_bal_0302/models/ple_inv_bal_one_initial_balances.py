from odoo import fields, models, api
import datetime
from dateutil.relativedelta import relativedelta
import base64
from odoo.exceptions import ValidationError


class PleInvBal1One(models.Model):
    _inherit = 'ple.report.inv.bal.one'

    line_initial_ids = fields.One2many(
        comodel_name='ple.inv.bal.one.line.initial.balances',
        inverse_name='ple_report_inv_val_one_id',
        string='Líneas'
    )

    line_final_ids = fields.One2many(
        comodel_name='ple.inv.bal.one.line.final.balances',
        inverse_name='ple_report_inv_val_one_id',
        string='Líneas'
    )

    def action_generate_initial_whit_ending_balances(self):
        data = False
        documents = self.env['ple.report.inv.bal.one'].search([
            ('date_start', '>=', self.date_start - relativedelta(years=1)),
            ('date_end', '<=', self.date_start),
            ('company_id', '=', self.company_id.id),
            ('state', 'in', ('load', 'closed')),
        ], limit=1)
        if documents:
            data = True
            self.write({
                'line_initial_ids': [(5, 0, 0)],
            })
            for obj_line in documents.line_final_ids:
                if obj_line['balance'] != 0.00:
                    self.write({
                        'line_initial_ids': [
                            (0, 0, {'period': self.date_end.strftime('%Y%m%d') or '',
                                    'accounting_account': obj_line['accounting_account'],
                                    'bank_account_name': obj_line['bank_account_name'],
                                    'type_currency': obj_line['type_currency'],
                                    'balance': obj_line['balance'],
                                    'status': '1',
                                    'note': obj_line['note'],
                                    'bic': obj_line['bic'],
                                    'account_bank_code': obj_line['account_bank_code'],
                                    'sequence': obj_line['sequence'],
                                    'account_ids': obj_line['account_ids'],
                                    'ple_report_inv_val_one_id': self.id,
                                    }),
                        ]
                    })

        return data

    def action_generate_initial_balances(self):
        self.line_initial_ids.unlink()
        company_id = self.company_id.id
        date_start = self.date_start
        date_end = self.date_end

        account_ids = """
            SELECT
                account_account.id,
                group_id,
                account_account.code,
                account_account.name,
                res_currency.name AS type_currency,
                sunat_bank_code,
                acc_number
            -- QUERIES TO MATCH MULTI TABLES      
            FROM account_account

            --  TYPE JOIN   |  TABLE                        | MATCH
                INNER JOIN      account_group               ON (account_group.id = account_account.group_id)
                LEFT JOIN       res_partner_bank            ON (account_account.bank_id = res_partner_bank.id)
                LEFT JOIN       res_bank                    ON (res_partner_bank.bank_id = res_bank.id)
                LEFT JOIN      res_currency                ON (account_account.currency_id = res_currency.id)

            -- FILTER QUERIES 
            WHERE account_group.code_prefix_start = '10'
                AND account_account.company_id IS NOT NULL
            """

        group_10 = f"""
                SELECT
                    account_id, 
                    account_move_line.balance

                -- QUERIES TO MATCH MULTI TABLES
                FROM account_move as am, account_move_line

                -- FILTER QUERIES 
                WHERE(account_move_line.move_id = am.id)
                AND(
                        (
                            (
                                ( (account_move_line.date >= '{date_start - relativedelta(years=1)}') AND  (account_move_line.date <= '{date_end  - relativedelta(years=1)}'))
                            AND  (account_move_line.company_id = {company_id}))
                        AND am.state = 'posted')
                    AND(account_move_line.account_id in (SELECT ids.id FROM ({account_ids}) AS ids)))
                AND(account_move_line.company_id IS NULL OR(account_move_line.company_id in ({company_id})))
                """

        query = f"""
            SELECT
                SUM(group_10.balance) AS balance,
                replace(lines.code, '.', '') AS accounting_account,
                lines.name AS bank_account_name,
                CASE WHEN replace(lines.code, '.', '')  IN ('1030001', '1051000', '1051002') THEN
                    lines.type_currency
                    ELSE (
                        CASE WHEN lines.type_currency IS NOT NULL THEN                    
                            lines.type_currency
                            ELSE 'PEN'
                        END
                    )
                END AS type_currency,
                CASE WHEN lines.sunat_bank_code IS NOT NULL THEN
                    lines.sunat_bank_code ELSE '99'        
                END AS bic,
                CASE WHEN lines.sunat_bank_code != '99' THEN
                    lines.acc_number ELSE '-'
                END AS account_bank_code

            -- QUERIES TO MATCH MULTI TABLES
            FROM (({account_ids}) AS lines 

            --  TYPE JOIN               |  TABLE                        | MATCH    
                INNER JOIN ({group_10}) AS group_10                     ON lines.id = group_10.account_id)

            -- GROUP DATA
            GROUP BY
                lines.name,
                lines.type_currency,
                lines.sunat_bank_code,
                lines.acc_number,
                accounting_account
            """

        try:

            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
            ids =(self.env['ple.inv.bal.one.line.initial.balances'].create(result)).ids
            self.line_initial_ids = ids

        except Exception as error:
            raise ValidationError(f'Error al ejecutar queries, comunciar al administrador: \n {error}')

    def action_compute_initial_balance_302(self):
        data = self.action_generate_initial_whit_ending_balances()
        if data:
            pass
        else:
            self.action_generate_initial_balances()
        return

    def capture_initial_balances_id(self):
        quantity_hand = dict()
        for obj in self.line_initial_ids:
            quantity_hand[obj.accounting_account] = {}
            quantity_hand[obj.accounting_account]['period'] = obj.period
            quantity_hand[obj.accounting_account]['bank_account_name'] = obj.bank_account_name
            quantity_hand[obj.accounting_account]['type_currency'] = obj.type_currency
            quantity_hand[obj.accounting_account]['balance'] = obj.balance
            quantity_hand[obj.accounting_account]['status'] = obj.bic
            quantity_hand[obj.accounting_account]['note'] = obj.note
            quantity_hand[obj.accounting_account]['bic'] = obj.bic
            quantity_hand[obj.accounting_account]['account_bank_code'] = obj.account_bank_code
            quantity_hand[obj.accounting_account]['sequence'] = obj.sequence
            quantity_hand[obj.accounting_account]['ple_report_inv_val_one_id'] = obj.ple_report_inv_val_one_id
            quantity_hand[obj.accounting_account]['account_ids'] = obj.account_ids
        return quantity_hand


class PleInvBal1OneLinesInitial(models.Model):
    _name = 'ple.inv.bal.one.line.initial.balances'
    _description = 'Efectivo y Equivalente de efectivo de saldos iniciales - Líneas'
    _order = 'sequence desc'

    period = fields.Char(string="Periodo")
    accounting_account = fields.Char(string="Cuenta contables")
    bank_account_name = fields.Char(string="Nombre de la cuenta bancaria")
    type_currency = fields.Char(string="Tipo de Moneda")
    balance = fields.Float(string="Saldo")
    credit_balance = fields.Float(string="Saldo acreedor", compute="_onchange_credit_balance")
    debit_balance = fields.Float(string="Saldo Deudor", compute="_onchange_debit_balance")
    status = fields.Char(string="Estado")
    note = fields.Char(string="Nota")
    bic = fields.Char(string="Codigo de la Entidad Financiera")
    account_bank_code = fields.Char(string="Número de la cuenta de la Entidad Financiera")
    sequence = fields.Integer(string='Secuencia')
    ple_report_inv_val_one_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.one',
        string='Reporte de Estado de Situación financiera'
    )
    account_ids = fields.Many2many(
        comodel_name='account.move.line',
        string='Cuentas',
        readonly=1
    )
    @api.depends('balance')
    def _onchange_credit_balance(self):
        for record in self:
            record.credit_balance = -record.balance if record.balance <= 0.00 else 0.00

    @api.depends('balance')
    def _onchange_debit_balance(self):
        for record in self:
            record.debit_balance = record.balance if record.balance > 0.00 else 0.00


class PleInvBal1OneLinesFinal(models.Model):
    _name = 'ple.inv.bal.one.line.final.balances'
    _description = 'Efectivo y Equivalente de efectivo de saldos iniciales - Líneas'
    _order = 'sequence desc'

    period = fields.Char(string="Periodo")
    accounting_account = fields.Char(string="Cuenta contables")
    bank_account_name = fields.Char(string="Nombre de la cuenta bancaria")
    type_currency = fields.Char(string="Tipo de Moneda")
    balance = fields.Float(string="Saldo")
    credit_balance = fields.Float(string="Saldo acreedor", compute="_onchange_credit_balance")
    debit_balance = fields.Float(string="Saldo Deudor", compute="_onchange_debit_balance")
    status = fields.Char(string="Estado")
    note = fields.Char(string="Nota")
    bic = fields.Char(string="Codigo de la Entidad Financiera")
    account_bank_code = fields.Char(string="Número de la cuenta de la Entidad Financiera")
    sequence = fields.Integer(string='Secuencia')

    ple_report_inv_val_one_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.one',
        string='Reporte de Estado de Situación financiera'
    )
    account_ids = fields.Many2many(
        comodel_name='account.move.line',
        string='Cuentas',
        readonly=1
    )

    @api.depends('balance')
    def _onchange_credit_balance(self):
        for record in self:
            record.credit_balance = record.balance if record.balance <= 0.00 else 0.00

    @api.depends('balance')
    def _onchange_debit_balance(self):
        for record in self:
            record.debit_balance = record.balance if record.balance > 0.00 else 0.00
