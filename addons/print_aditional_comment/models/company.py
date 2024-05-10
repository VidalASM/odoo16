from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    additional_information = fields.Html(string='Información Adicional Factura impresa')
