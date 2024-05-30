from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    efemd_ple_id = fields.Many2one(
        string='3.18 Rubro EFEMD',
        comodel_name='eeff.ple',
        related='account_id.efemd_category',
        store=True
    )
