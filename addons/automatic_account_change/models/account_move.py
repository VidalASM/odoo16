from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    pay_sell_force_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Forzar cuenta por cobrar o pagar'
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        super()._onchange_partner_id()
        self._get_change_account()

    @api.onchange('invoice_line_ids')
    def _onchange_quick_edit_line_ids(self):
        super()._onchange_quick_edit_line_ids()
        self._get_change_account()

    @api.onchange('currency_id') 
    def _onchange_currency_change_account(self):
        self._get_change_account()

    def _get_change_account(self):
        if self.journal_id and self.currency_id:
            account_output = False
            if self.pay_sell_force_account_id:
                if self.move_type in ['out_invoice', 'out_refund']:
                    account_output = self.pay_sell_force_account_id.sale_account_id
                elif self.move_type in ['in_invoice', 'out_refund']:
                    account_output = self.pay_sell_force_account_id.purchase_account_id
            else:
                account_change = self.env['account.change.by.type'].search([
                    ('journal_id', '=', self.journal_id.id),
                    ('currency_id', '=', self.currency_id.id)
                ], limit=1)
                if account_change:
                    if self.move_type in ['out_invoice', 'out_refund']:
                        account_output = account_change.sale_account_id
                    elif self.move_type in ['in_invoice', 'in_refund']:
                        account_output = account_change.purchase_account_id

            if account_output:
                for line in self.line_ids:
                    if line.display_type == 'payment_term':
                        line.update({'account_id': account_output.id})

    def write(self, vals):
        res = super().write(vals)
        for move in self:
            move.with_context(tracking_disable=True)._get_change_account()
        return res
