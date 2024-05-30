from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_aggregated_product_quantities(self, **kwargs):
        """ Returns a dictionary of products add weight (key = id+name+description+uom+weight) and corresponding values of interest."""
        res = super(StockMoveLine, self)._get_aggregated_product_quantities()

        for move_line in res.values():
            move_line["weight"] = move_line["product"].weight

        return res

class StockLocation(models.Model):
    _inherit = 'stock.location'

    direction_id = fields.Many2one(
        comodel_name='res.partner',
        string='Dirección',
        compute='_default_direction_id',
        inverse='_inverse_direction_id',
        default=False,
        store=True
    )

    @api.depends('warehouse_id.partner_id', 'active')
    def _default_direction_id(self):
        for record in self:
            if record.active and record.warehouse_id and record.warehouse_id.partner_id:
                record.direction_id = record.warehouse_id.partner_id
            else:
                record.direction_id = False

    def _inverse_direction_id(self):
        return