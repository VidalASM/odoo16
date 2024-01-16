#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.is_downpayment:
            invoice_lines = self.invoice_lines.filtered(
                lambda x: x.parent_state == "posted"
            )
            res["l10n_pe_edi_advance_serie"] = (
                invoice_lines
                and str(invoice_lines[0].move_id.sequence_prefix)[0:4]
                or ""
            )
            res["l10n_pe_edi_advance_number"] = (
                invoice_lines and invoice_lines[0].move_id.sequence_number or 0
            )
        return res
