from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    weight = fields.Float(
        string="Peso Neto",
        help="Peso neto",
        related='product_tmpl_id.weight',
        store=True,
        readonly=False)

    gross_weight = fields.Float(
        string="Peso Bruto",
        help="Peso bruto",
        related='product_tmpl_id.gross_weight',
        store=True,
        readonly=False)
