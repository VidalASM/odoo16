from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move.line'

    origin_address = fields.Many2one('res.partner', string='Dirección de origen')
    destiny_address = fields.Many2one('res.partner', string='Dirección de destino')
