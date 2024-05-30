from odoo import fields, models


class AccountSpotDetraction(models.Model):
    _inherit = 'account.spot.detraction'

    code = fields.Char(
        string='Código',
        required=True
    )
    rate = fields.Float(
        string="Tasa %",
        required=True
    )
