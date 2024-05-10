from odoo import api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    picking_number = fields.Char(
        string='N° Guía',
        copy=False
    )

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('form'):
            tags = ['picking_number']
            arch, view = self.env['res.partner']._tags_invisible_per_country(arch, view, tags, [self.env.ref('base.pe')])
        return arch, view
