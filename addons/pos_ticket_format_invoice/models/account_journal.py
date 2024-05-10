# odoo
from odoo import api, fields, models


class AccountJounal(models.Model):
    _inherit = 'account.journal'

    address_point_emission = fields.Char('Dirección punto de emisión')
