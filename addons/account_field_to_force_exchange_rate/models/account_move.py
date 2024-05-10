from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    to_force_exchange_rate = fields.Float(
        string='Forzar T.C.',
        digits=0,
        help='Este campo se utiliza para forzar el tipo de cambio.'
    )

    @api.depends('currency_id', 'company_id', 'date', 'invoice_date', 'to_force_exchange_rate')
    def _compute_currency_rate(self):
        super()._compute_currency_rate()

    def _get_actual_currency_rate(self):
        if self.currency_id and self.currency_id != self.company_currency_id and self.to_force_exchange_rate != 0.0:
            return 1 / self.to_force_exchange_rate
        return super()._get_actual_currency_rate()

    def action_register_payment(self):
        action = super().action_register_payment()
        if len(self) == 1:
            action['context']['to_force_exchange_rate'] = self.to_force_exchange_rate
        return action

    @api.onchange('currency_id', 'company_id', 'to_force_exchange_rate')
    def _onchange_to_force_exchange_rate(self):
        if self.currency_id == self.company_currency_id:
            self.to_force_exchange_rate = 0.0

    @api.onchange('currency_id', 'to_force_exchange_rate')
    def _onchange_currency_move_type_entry(self):
        if self.currency_id and self.move_type == 'entry':
            self.line_ids._inverse_amount_currency()
