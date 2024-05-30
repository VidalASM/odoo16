from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    exchange_rate = fields.Float(
        string='Tipo de Cambio',
        digits=0,
        compute='_compute_currency_rate',
        store=True
    )

    @api.depends('currency_id', 'company_id', 'date', 'invoice_date')
    def _compute_currency_rate(self):
        for move in self:
            move.exchange_rate = move._get_actual_currency_rate()

    def _get_actual_currency_rate(self):
        if not self.currency_id:
            return 1.0

        inverse_exchange_rate = self.env['res.currency']._get_conversion_rate(
            from_currency=self.company_currency_id,
            to_currency=self.currency_id,
            company=self.company_id,
            date=self.date or self.invoice_date or fields.Date.context_today(self),
        )
        return 1 / inverse_exchange_rate
