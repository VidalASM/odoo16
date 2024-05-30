from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    account_value_unit = fields.Float(
        compute="_compute_account_value_unit_purchase_order", 
        string='Valor Unitario',
        digits='Product Price'
    )

    @api.depends('account_value_unit', 'price_unit', 'taxes_id')
    def _compute_account_value_unit_purchase_order(self):
        for line in self:
            data = []
            data = [rec.amount for rec in line.taxes_id]
            if not data:
                line.account_value_unit = 0.0
            elif 18.0 in data:
                line.account_value_unit = line.price_unit / 1.18
            else:
                dato = max(data) / 100
                line.account_value_unit = line.price_unit / (1 + dato)
