from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    efemd_category = fields.Many2one(
        string='3.18 Rubro EFEMD',
        comodel_name='eeff.ple'
    )
