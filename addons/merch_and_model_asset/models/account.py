from odoo import api, fields, models,_


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    asset_brand = fields.Char(
        string="Marca"
    )
    asset_model = fields.Char(
        string="Modelo",
    )
    asset_series = fields.Char(
        string="N° de Serie y/o Placa"
    )

    def open_asset(self, view_mode):
        asset_type = self.asset_type if len(self) == 1 else self[0].asset_type
        views = [v for v in self._get_views(asset_type) if v[1] in view_mode]

        ctx = dict(self._context,
                   asset_type=asset_type,
                   default_asset_type=asset_type)

        if 'default_move_type' in ctx.keys():
            ctx.pop('default_move_type')

        action = {
            'name': _('Asset'),
            'view_mode': ','.join(view_mode),
            'type': 'ir.actions.act_window',
            'res_id': self.id if 'tree' not in view_mode else False,
            'res_model': 'account.asset',
            'views': views,
            'domain': [('id', 'in', self.ids)],
            'context': ctx
        }
        if asset_type == 'sale':
            action['name'] = _('Deferred Revenue')
        elif asset_type == 'expense':
            action['name'] = _('Deferred Expense')

        return action

