from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends(
        'currency_id',
        'company_id',
        'move_id.date',
        'move_id.invoice_date',
        'move_id.to_force_exchange_rate'
    )
    def _compute_currency_rate(self):
        super()._compute_currency_rate()
        for line in self:
            if line.currency_id and line.currency_id != line.company_currency_id and line.move_id.to_force_exchange_rate != 0.0:
                line.currency_rate = line.move_id.to_force_exchange_rate

    # @override
    @api.depends('move_id.currency_id')
    def _compute_currency_id(self):
        for line in self:
            if line.display_type == 'cogs':
                line.currency_id = line.company_currency_id
            elif line.move_id.is_invoice(include_receipts=True):
                line.currency_id = line.move_id.currency_id
            elif line.move_id.move_type == 'entry':
                line.currency_id = line.move_id.currency_id
            else:
                line.currency_id = line.currency_id or line.company_id.currency_id
