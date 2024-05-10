from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    legal_representative = fields.Many2one(
        comodel_name='res.partner',
        string="Representante Legal"
    )

    object_company = fields.Text(
        string="Objeto"
    )
