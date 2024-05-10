from odoo import fields, models

class AccountAccount(models.Model):
    _inherit = 'account.account'

    eri_ple_id = fields.Many2one(
        string='3.24 Rubro ERI',
        comodel_name='eeff.ple'
    )
    

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    eri_ple_id = fields.Many2one(
        string='3.24 Rubro ERI',
        comodel_name='eeff.ple',
        related='account_id.eri_ple_id',
        store=True
    )
