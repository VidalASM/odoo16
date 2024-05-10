from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    cod_client_sucur = fields.Char(
        string="Código Cliente/Sucursal", help="Código del CLiente y su Sucursal"
    )