from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, date=None):
        move = super()._create_invoices(grouped, final, date)
        move.with_context(tracking_disable=True)._get_change_account()
        return move
