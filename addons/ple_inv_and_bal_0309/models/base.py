from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    ple_selection = fields.Selection(
        selection_add=[
            ('investment_active_intangible_3_9',
             '3.9 Registro de Inventarios y Balances - Activos Intangibles - Activo'),
            ('investment_active_intangible_deprecated_3_9',
             '3.9 Registro de Inventarios y Balances - Activos Intangibles - Amortizacition acumulada')
        ])


class InventoryAndBalances09(models.Model):
    _name = 'inventory.and.balances.09'
    _description = 'Inventario y Balance PLE 09'

    accounting_seat_09 = fields.Many2one(
        string='Asiento contable',
        comodel_name='account.move.line',
        domain=[('account_id.ple_selection', '=',
                 'investment_active_intangible_deprecated_3_9')]
    )
    provision_account_09 = fields.Many2one(
        string='Cuenta de provisión',
        comodel_name='account.account'
    )
    account_date_ple_09 = fields.Date(string="Fecha")
    amount_balance_09 = fields.Float(string="Monto")
    account_move_line_ids_09 = fields.Many2one(
        'account.move.line', string="Account Move Line")

    @api.onchange('accounting_seat_09')
    def onchange_accounting_seat_09(self):
        if self.accounting_seat_09:
            self.provision_account_09 = self.accounting_seat_09.account_id
            self.account_date_ple_09 = self.accounting_seat_09.move_id.date
            self.amount_balance_09 = self.accounting_seat_09.balance


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    inventory_and_balances_line_ids_09 = fields.One2many(
        'inventory.and.balances.09', 'account_move_line_ids_09', string="Inventario y Balances")
