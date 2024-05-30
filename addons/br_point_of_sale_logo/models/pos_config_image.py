from odoo import models, fields


class PosConfigImage(models.Model):
    _inherit = 'pos.config'

    image = fields.Binary(string='Image')
