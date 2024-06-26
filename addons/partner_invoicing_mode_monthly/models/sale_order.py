# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models
from odoo.osv.expression import OR


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def cron_generate_monthly_invoices(self):
        """Cron called daily to check if monthly invoicing needs to be done."""
        company_ids = self._company_monthly_invoicing_today()
        if company_ids:
            self.generate_monthly_invoices(company_ids)

    @api.model
    def generate_monthly_invoices(self, companies=None):
        """Generate monthly invoices for customers who require that mode.

        Invoices will be generated by other jobs split for different customer
        and different payment term.
        """
        if companies is None:
            companies = self.env.company
        saleorder_groups = self.read_group(
            [
                ("invoicing_mode", "=", "monthly"),
                ("invoice_status", "=", "to invoice"),
                ("company_id", "in", companies.ids),
            ],
            ["partner_invoice_id"],
            groupby=self._get_groupby_fields_for_monthly_invoicing(),
            lazy=False,
        )
        for saleorder_group in saleorder_groups:
            saleorder_ids = self.search(saleorder_group["__domain"]).ids
            self.with_delay()._generate_invoices_by_partner(saleorder_ids)
        companies.write({"invoicing_mode_monthly_last_execution": datetime.now()})
        return saleorder_groups

    @api.model
    def _get_groupby_fields_for_monthly_invoicing(self):
        """Returns the sale order fields used to group them into jobs."""
        return ["partner_invoice_id", "payment_term_id"]

    def _generate_invoices_by_partner(self, saleorder_ids, invoicing_mode="monthly"):
        """Generate invoices for a group of sale order belonging to a customer."""
        sales = (
            self.browse(saleorder_ids)
            .exists()
            .filtered(lambda r: r.invoice_status == "to invoice")
        )
        if not sales:
            return "No sale order found to invoice ?"
        invoices = sales._create_invoices(
            grouped=sales[0].partner_invoice_id.one_invoice_per_order, final=True
        )
        for invoice in invoices:
            invoice.with_delay()._validate_invoice()
        return invoices

    @api.model
    def _company_monthly_invoicing_today(self):
        """Get company ids for which today is monthly invoicing day."""
        today = datetime.now()
        first_day_this_month = today.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        first_day_last_month = first_day_this_month - relativedelta(months=1)
        last_day_of_this_month = (today + relativedelta(day=31)).day
        # Last month still not executed, it needs to be done
        domain_last_month = [
            ("invoicing_mode_monthly_last_execution", "<", first_day_last_month),
        ]
        # Invoicing day is today or in the past and invoicing not yet done
        domain_this_month = [
            "|",
            ("invoicing_mode_monthly_last_execution", "<", first_day_this_month),
            ("invoicing_mode_monthly_last_execution", "=", False),
            ("invoicing_mode_monthly_day_todo", "<=", today.day),
        ]
        # Make sure non exisiting days are done at the end of the month
        domain_last_day_of_month = [
            "|",
            ("invoicing_mode_monthly_last_execution", "<", first_day_this_month),
            ("invoicing_mode_monthly_last_execution", "=", False),
            ("invoicing_mode_monthly_day_todo", ">", today.day),
        ]
        if today.day == last_day_of_this_month:
            domain = OR(
                [domain_last_month, domain_this_month, domain_last_day_of_month]
            )
        else:
            domain = OR([domain_last_month, domain_this_month])

        return self.env["res.company"].search(domain)
