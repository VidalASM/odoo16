from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    to_force_exchange_rate = fields.Float(
        string='Forzar T.C.',
        digits=0,
        help='Este campo se utiliza para forzar el tipo de cambio.'
    )

    @api.onchange('currency_id', 'company_id', 'to_force_exchange_rate')
    def _onchange_to_force_exchange_rate(self):
        if self.currency_id == self.company_currency_id:
            self.to_force_exchange_rate = 0.0

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        line_vals_list = super()._prepare_move_line_default_vals(write_off_line_vals)

        if self.currency_id and self.currency_id != self.company_currency_id and self.to_force_exchange_rate != 0.0:

            for line_vals in line_vals_list:
                liquidity_amount_currency = line_vals.get('amount_currency', 0.0)
                liquidity_balance = self.currency_id._force_convert(
                    liquidity_amount_currency,
                    self.company_id.currency_id,
                    self.company_id,
                    self.to_force_exchange_rate
                )
                line_vals.update({
                    'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                    'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                })

        return line_vals_list
