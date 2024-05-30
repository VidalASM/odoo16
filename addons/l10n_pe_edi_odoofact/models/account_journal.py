#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _default_l10n_latam_document_type_id(self):
        if self.type == "sale" and self.company_id.country_id.code == "PE":
            return (
                self.env["l10n_latam.document.type"]
                .search([("internal_type", "=", "invoice")], limit=1)
                .id
            )
        return False

    def _default_l10n_pe_edi_shop_id(self):
        return (
            self.env["l10n_pe_edi.shop"]
            .search([("company_id", "=", self.env.company.id)], limit=1)
            .id
        )

    l10n_latam_document_type_id = fields.Many2one(
        comodel_name="l10n_latam.document.type",
        string="Document Type",
        default=_default_l10n_latam_document_type_id,
    )
    l10n_pe_edi_shop_id = fields.Many2one(
        comodel_name="l10n_pe_edi.shop",
        string="Shop",
        default=_default_l10n_pe_edi_shop_id,
    )
    l10n_pe_edi_is_einvoice = fields.Boolean(string="Is E-invoice")
    l10n_pe_edi_contingency = fields.Boolean(
        string="Contingency", help="Check this for contingency invoices"
    )
