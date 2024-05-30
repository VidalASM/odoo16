###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    def _default_invoice_journal_ids(self):
        return self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.env.company.id)], limit=1
        )

    l10n_pe_edi_send_invoice = fields.Boolean(
        string="Electronic Invoicing",
        related="company_id.l10n_pe_edi_send_invoice",
        readonly=True,
    )
    invoice_journal_ids = fields.Many2many(
        "account.journal",
        "pos_config_invoice_journal_rel",
        "config_id",
        "journal_id",
        "Accounting Invoice Journal",
        help="Invoice journals for Electronic invoices.",
        default=_default_invoice_journal_ids,
    )
    default_partner_id = fields.Many2one(
        "res.partner",
        string="Client by default",
        help="This client will be set by default in the order",
    )
    auto_check_invoice = fields.Boolean(string="Auto create Invoice")

    receipt_design = fields.Many2one("pos.receipt", help="Choose any receipt design")
    design_receipt = fields.Text(
        related="receipt_design.design_receipt", string="Receipt XML"
    )
    is_custom_receipt = fields.Boolean()

    @api.onchange("l10n_pe_edi_send_invoice")
    def _onchange_module_einvoice(self):
        self.auto_check_invoice = self.l10n_pe_edi_send_invoice
