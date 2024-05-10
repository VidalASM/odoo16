from odoo import api, fields, models
from odoo.osv import expression


class AssetIntangible(models.Model):
    _name = 'asset.intangible'
    _description = 'Asset / Intangible'

    name = fields.Char(
        string='Asset / Intangible'
    )
    bool_asset_intagible = fields.Boolean(
        string='is the asset / intangible active',
    )
    operation_date = fields.Date(string='Operation date the asset')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = [('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    asset_intangible_id = fields.Many2one(
        comodel_name='asset.intangible',
        string='Asset / Intangible')
