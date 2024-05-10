from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    weight = fields.Float(string="Peso Neto", help="Peso neto")
    gross_weight = fields.Float(string="Peso Bruto", help="Peso bruto")
    product_variant_ids = fields.One2many(
        comodel_name="product.product",
        inverse_name="product_tmpl_id",
        string="Variants",
    )
