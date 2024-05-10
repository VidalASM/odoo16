from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_view_invoice(self, invoices=False):
        if not invoices:
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids
        for invoice in invoices:
            invoice.with_context(tracking_disable=True)._get_change_account()
        res = super().action_view_invoice(invoices)
        return res
