from odoo import fields, models
from odoo.tools.translate import xml_translate


class PosReceipt(models.Model):
    _name = "pos.receipt"

    name = fields.Char()
    design_receipt = fields.Text(
        string="Receipt XML",
        help="Add your customised receipts for pos",
        translate=xml_translate,
    )
