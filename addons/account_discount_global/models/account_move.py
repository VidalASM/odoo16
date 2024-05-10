from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    discount_percent_global = fields.Float(
        string='Descuento Global %',
        compute='_compute_discount_percent_global',
        store=True
    )

    @api.depends(
        'invoice_line_ids.product_id',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
    )
    def _compute_discount_percent_global(self):
        for move in self:
            price_subtotal_with_discount = 0.0
            price_subtotal_without_discount = 0.0

            for line in move.invoice_line_ids:
                if move.is_invoice(True):
                    if line.product_id.global_discount and line.price_subtotal < 0:
                        price_subtotal_with_discount += line.price_subtotal

                    if not line.product_id.global_discount:
                        price_subtotal_without_discount += line.price_subtotal

            move.discount_percent_global = abs(price_subtotal_with_discount / max(price_subtotal_without_discount, 1) * 100)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    global_discount = fields.Boolean(
        string='Descuento Global'
    )
