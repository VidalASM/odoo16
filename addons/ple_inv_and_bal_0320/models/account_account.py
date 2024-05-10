from odoo import fields, models

class AccountAccount(models.Model):
    _inherit = 'account.account'

    eerr_ple_id = fields.Many2one(
        string='3.20 Rubro EERR',
        comodel_name='eeff.ple'
    )
    

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    eerr_ple_id = fields.Many2one(
        string='3.20 Rubro EERR',
        comodel_name='eeff.ple',
        related='account_id.eerr_ple_id',
        store=True
    )
