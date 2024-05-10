from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    partner_name = fields.Char(
        string='Nombre'
    )
    first_name = fields.Char(
        string='Apellido Paterno'
    )
    second_name = fields.Char(
        string='Apellido Materno'
    )
