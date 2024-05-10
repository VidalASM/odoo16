from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('currency_id', 'company_id', 'move_id.date', 'move_id.invoice_date')
    def _compute_currency_rate(self):
        super()._compute_currency_rate()
        for line in self:
            if line.currency_id:
                line.currency_rate = self.env['res.currency']._get_conversion_rate(
                    from_currency=line.company_currency_id,
                    to_currency=line.currency_id,
                    company=line.company_id,
                    date=line.move_id.date or line.move_id.invoice_date or fields.Date.context_today(line),
                )
