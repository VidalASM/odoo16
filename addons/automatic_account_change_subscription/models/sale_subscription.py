from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def _create_recurring_invoice(self, automatic=False, batch_size=30):
        invoices = super()._create_recurring_invoice(automatic, batch_size)
        for invoice in invoices:
            invoice.with_context(tracking_disable=True)._get_change_account()
        return invoices
