from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move.line'

    account_value_unit = fields.Float(
        compute="_compute_account_value_unit_account_move",
        string='Valor Unitario',
        digits='Product Price'
    )

    @api.depends('account_value_unit', 'price_unit', 'tax_ids')
    def _compute_account_value_unit_account_move(self):
        for line in self:
            data = []
            data = [rec.amount for rec in line.tax_ids]
            if not data:
                line.account_value_unit = 0.0
            elif 18.0 in data:
                line.account_value_unit = line.price_unit / 1.18
            else:
                dato = max(data) / 100
                line.account_value_unit = line.price_unit / (1 + dato)


