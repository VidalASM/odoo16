from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    aditional_document_reference = fields.Char(string='Otro tipo de documento')