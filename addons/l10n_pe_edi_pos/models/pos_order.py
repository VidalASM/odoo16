###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    invoice_journal_id = fields.Many2one(
        "account.journal", "Journal account", readonly=1
    )

    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        result["account_move_name"] = order.account_move.name
        return result

    def _prepare_invoice_vals(self):
        values = super(PosOrder, self)._prepare_invoice_vals()
        if self.config_id.l10n_pe_edi_send_invoice:
            if self.invoice_journal_id:
                values["journal_id"] = self.invoice_journal_id.id
        return values

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get("invoice_journal_id", False):
            order_fields["invoice_journal_id"] = ui_order.get("invoice_journal_id")
        return order_fields

    def get_move(self):
        self.ensure_one()
        qr_data = ""
        if self.company_id.vat:
            qr_data += "|" + str(self.company_id.vat)
            if (
                self.account_move.l10n_latam_document_type_id
                and self.account_move.l10n_latam_document_type_id.code
            ):
                qr_data += "|" + str(self.account_move.l10n_latam_document_type_id.code)
            if self.account_move.sequence_prefix:
                qr_data += "|" + str(self.account_move.sequence_prefix)[0:4]
            if self.account_move.sequence_number:
                qr_data += "|" + str(self.account_move.sequence_number)
            if self.account_move.l10n_pe_edi_amount_igv:
                qr_data += "|" + str(self.account_move.l10n_pe_edi_amount_igv)
            if self.account_move.amount_total:
                qr_data += "|" + str(self.account_move.amount_total)
            if self.account_move.invoice_date:
                qr_data += "|" + str(self.account_move.invoice_date)
            if (
                self.account_move.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code
            ):
                qr_data += "|" + str(
                    self.account_move.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code
                )
            if self.account_move.partner_id.vat:
                qr_data += "|" + str(self.account_move.partner_id.vat)
        return {
            "invoice_number": self.account_move.name,
            "type_of_invoice_document": (
                self.account_move.l10n_latam_document_type_id.name + " Electrónica"
            ).upper(),
            "igv_percent": self.account_move.l10n_pe_edi_igv_percent,
            "amount_in_words": self.account_move._get_amount_in_words(),
            "currency_name": (
                self.account_move.currency_id.currency_unit_label
                or self.account_move.currency_id.name
            ),
            "authorization_message": (
                self.company_id.l10n_pe_edi_ose_id
                and self.company_id.l10n_pe_edi_ose_id.authorization_message
                or ""
            ),
            "control_url": (
                self.company_id.l10n_pe_edi_ose_id
                and self.company_id.l10n_pe_edi_ose_id.control_url
                or "NO VALID"
            ),
            "date_invoice": self.account_move.invoice_date,
            "invoice_date_due": self.account_move.invoice_date_due,
            "barcode": qr_data,
        }

    @api.model
    def invoice_data(self, order):
        data = {}
        qr_data = ""
        try:
            pos_order = self.env["pos.order"].search([("pos_reference", "=", order)])
            if pos_order and pos_order.account_move:
                data["invoice_number"] = pos_order.account_move.name
                data["type_of_invoice_document"] = (
                    pos_order.account_move.l10n_latam_document_type_id.name
                    + " Electrónica"
                ).upper()
                data["igv_percent"] = pos_order.account_move.l10n_pe_edi_igv_percent
                data["amount_in_words"] = pos_order.account_move._get_amount_in_words()
                data["currency_name"] = (
                    pos_order.account_move.currency_id.currency_unit_label
                    or pos_order.account_move.currency_id.name
                )
                data["authorization_message"] = (
                    pos_order.company_id.l10n_pe_edi_ose_id
                    and pos_order.company_id.l10n_pe_edi_ose_id.authorization_message
                    or ""
                )
                data["control_url"] = (
                    pos_order.company_id.l10n_pe_edi_ose_id
                    and pos_order.company_id.l10n_pe_edi_ose_id.control_url
                    or "NO VALID"
                )
                data["date_invoice"] = pos_order.account_move.invoice_date
                data["invoice_date_due"] = pos_order.account_move.invoice_date_due
                if pos_order.company_id.vat:
                    qr_data += "|" + str(pos_order.company_id.vat)
                if (
                    pos_order.account_move.l10n_latam_document_type_id
                    and pos_order.account_move.l10n_latam_document_type_id.code
                ):
                    qr_data += "|" + str(
                        pos_order.account_move.l10n_latam_document_type_id.code
                    )
                if pos_order.account_move.sequence_prefix:
                    qr_data += "|" + str(pos_order.account_move.sequence_prefix)[0:4]
                if pos_order.account_move.sequence_number:
                    qr_data += "|" + str(pos_order.account_move.sequence_number)
                if pos_order.account_move.l10n_pe_edi_amount_igv:
                    qr_data += "|" + str(pos_order.account_move.l10n_pe_edi_amount_igv)
                if pos_order.account_move.amount_total:
                    qr_data += "|" + str(pos_order.account_move.amount_total)
                if pos_order.account_move.invoice_date:
                    qr_data += "|" + str(pos_order.account_move.invoice_date)
                partner = pos_order.account_move.partner_id
                if partner.l10n_latam_identification_type_id.l10n_pe_vat_code:
                    qr_data += "|" + str(
                        partner.l10n_latam_identification_type_id.l10n_pe_vat_code
                    )
                if partner.vat:
                    qr_data += "|" + str(partner.vat)
                base_url = (
                    self.env["ir.config_parameter"].sudo().get_param("web.base.url")
                )
                base_url + "/report/barcode/QR/" + qr_data
                data["barcode"] = qr_data

        except Exception:
            data = False
        return data
