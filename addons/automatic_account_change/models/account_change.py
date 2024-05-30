from odoo import api, fields, models, _


class AccountChangeByType(models.Model):
    _name = 'account.change.by.type'
    _description = 'Cambio de cuenta'
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario',
        required=True,
        domain="[('company_id', '=', company_id)]"
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        required=True
    )
    sale_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta Venta',
        required=True,
        domain="[('company_id', '=', company_id)]"
    )
    purchase_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta Compra',
        required=True,
        domain="[('company_id', '=', company_id)]"
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        required=True,
        readonly=True,
        default=lambda self: self.env.company
    )
