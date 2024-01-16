#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

import json

import requests
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EdiRequest(models.Model):
    _name = "l10n_pe_edi.request"
    _description = "EDI Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _check_company_auto = True

    def _get_selection_document_type(self):
        return [
            ("01", "Factura"),
            ("03", "Boleta"),
            ("07", "Nota de Crédito"),
            ("08", "Nota de Débito"),
            ("20", "Comprobante de retención"),
            ("40", "Comprobante de percepción"),
            ("09", "Guía de Remisión Remitente"),
            ("31", "Guía de Remisión Transportista"),
        ]

    name = fields.Char(
        string="Description", size=128, index=True, required=True, default="New"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    document_date = fields.Date()
    document_number = fields.Char()
    l10n_pe_edi_shop_id = fields.Many2one(
        comodel_name="l10n_pe_edi.shop", string="Shop"
    )
    l10n_pe_edi_document_type = fields.Selection(
        selection="_get_selection_document_type", string="Document Type"
    )
    l10n_pe_edi_document_type_id = fields.Many2one(
        comodel_name="l10n_pe_edi.request.document.type",
        string="Request Document Type",
        compute="_compute_l10n_pe_edi_document_type_id",
        store=True,
        readonly=False,
    )
    model = fields.Char(string="Model Name")
    res_id = fields.Integer(
        string="Record ID", help="ID of the target record in the database"
    )
    reference = fields.Char(compute="_compute_reference")
    log_ids = fields.One2many(
        comodel_name="l10n_pe_edi.request.log",
        inverse_name="request_id",
        string="EDI logs",
        copy=False,
    )
    log_id = fields.Many2one(
        comodel_name="l10n_pe_edi.request.log",
        string="EDI log",
        compute="_compute_log_id",
        copy=False,
        store=True,
    )
    link_document = fields.Char(
        string="Invoice link", related="log_id.link_document", store=True
    )
    link_pdf = fields.Char(string="PDF link", related="log_id.link_pdf", store=True)
    link_xml = fields.Char(string="XML link", related="log_id.link_xml", store=True)
    link_cdr = fields.Char(string="CDR link", related="log_id.link_cdr", store=True)
    response = fields.Text(
        string="Response", related="log_id.response", store=True, tracking=True
    )
    ose_accepted = fields.Boolean(
        string="Sent to PSE/OSE",
        related="log_id.ose_accepted",
        store=True,
        tracking=True,
    )
    sunat_accepted = fields.Boolean(
        string="Accepted by SUNAT",
        related="log_id.sunat_accepted",
        store=True,
        tracking=True,
    )
    sunat_canceled = fields.Boolean(
        string="Canceled by SUNAT",
        related="log_id.sunat_canceled",
        store=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "New"),
            ("sent", "Sent to PSE/OSE"),
            ("accepted", "Accepted by SUNAT"),
        ],
        default="draft",
        tracking=True,
        compute="_compute_state",
        store=True,
    )
    l10n_pe_edi_cron_send_count = fields.Integer(
        string="Cron send count available",
        default=5,
        copy=False,
        help="Number of attempts available for sending e-invoices by the Cron",
    )
    l10n_pe_edi_cron_check_count = fields.Integer(
        string="Cron check count available",
        default=5,
        copy=False,
        help="Number of attempts available for checking e-invoices by the Cron",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("l10n_pe_edi.request") or "/"
                )
        return super(EdiRequest, self).create(vals)

    @api.depends("model", "res_id")
    def _compute_reference(self):
        for rec in self:
            rec.reference = "%s,%s" % (rec.model, rec.res_id)

    @api.depends("log_ids")
    def _compute_log_id(self):
        for rec in self:
            rec.log_id = rec.log_ids and rec.log_ids[0].id or False

    @api.depends("ose_accepted", "sunat_accepted")
    def _compute_state(self):
        for rec in self:
            if rec.sunat_accepted:
                rec.state = "accepted"
                continue
            if rec.ose_accepted:
                rec.state = "sent"
            else:
                rec.state = "draft"

    @api.depends("l10n_pe_edi_document_type")
    def _compute_l10n_pe_edi_document_type_id(self):
        for rec in self:
            doc_type_id = self.env["l10n_pe_edi.request.document.type"].search(
                [("code", "=", rec.l10n_pe_edi_document_type)], limit=1
            )
            rec.l10n_pe_edi_document_type_id = doc_type_id and doc_type_id.id or False

    def action_api_connect(self, operation):
        document = self.env[self.model].browse(self.res_id)
        document.check_data_to_send()
        vals = getattr(
            document,
            "_get_document_values_%s_%s"
            % (operation, self.l10n_pe_edi_shop_id.l10n_pe_edi_ose_code),
        )(self.l10n_pe_edi_shop_id.l10n_pe_edi_ose_code)
        getattr(
            self, "api_connector_%s" % self.l10n_pe_edi_shop_id.l10n_pe_edi_ose_code
        )(vals)
        self.env.cr.commit()

    def api_connector_odoofact(self, vals):
        data = json.dumps(vals)
        if (
            not self.l10n_pe_edi_shop_id.l10n_pe_edi_ose_url
            or not self.l10n_pe_edi_shop_id.l10n_pe_edi_ose_token
        ):
            raise UserError(_("The connection data with nubefact are not registered"))
        nubefact_url = self.l10n_pe_edi_shop_id.l10n_pe_edi_ose_url
        nubefact_token = self.l10n_pe_edi_shop_id.l10n_pe_edi_ose_token
        headers = {"Content-type": "application/json", "Authorization": nubefact_token}
        try:
            nubefact_request = requests.post(
                nubefact_url, data, headers=headers, verify=True, timeout=10
            )
            response = nubefact_request.text
            response = response.replace("'", "'")
            response = json.loads(response)
        except requests.exceptions.RequestException as e:
            response = {"errors": e}
        ose_accepted = False if response.get("errors", False) else True
        json_invoice = json.loads(data)
        self.env["l10n_pe_edi.request.log"].create(
            {
                "request_id": self.id,
                "json_sent": json.dumps(json_invoice, indent=4, sort_keys=True),
                "json_response": json.dumps(response, indent=4, sort_keys=True),
                "ose_accepted": ose_accepted,
                "sunat_accepted": response.get("aceptada_por_sunat", False),
                "sunat_canceled": response.get("anulado", False),
                "operation_type": json_invoice.get("operacion", False),
                "link_document": response.get("enlace", False),
                "link_pdf": response.get("enlace_del_pdf", False),
                "link_xml": response.get("enlace_del_xml", False),
                "link_cdr": response.get("enlace_del_cdr", False),
                "response": response.get("errors", False),
                "sunat_description": response.get("sunat_description", False),
                "sunat_note": response.get("sunat_note", False),
                "sunat_responsecode": response.get("sunat_responsecode", False),
                "sunat_soap_error": response.get("sunat_soap_error", False),
            }
        )

    def action_document_send(self):
        self.ensure_one()
        if self.model and self.res_id:
            record = self.env[self.model].browse(self.res_id)
            record.action_document_send()

    def action_document_check(self):
        self.ensure_one()
        if self.model and self.res_id:
            record = self.env[self.model].browse(self.res_id)
            record.action_document_check()

    def action_open_edi_request(self):
        """
        This method opens the EDI request
        """
        self.ensure_one()
        return {
            "view_mode": "form",
            "res_model": "l10n_pe_edi.request",
            "res_id": self.id,
            "type": "ir.actions.act_window",
        }

    def action_open_document(self):
        """
        This method opens the related electronic document
        """
        self.ensure_one()
        if self.model and self.res_id:
            return {
                "view_mode": "form",
                "res_model": self.model,
                "res_id": self.res_id,
                "type": "ir.actions.act_window",
            }
        return True

    def cron_send_documents(self):
        company_ids = self.env["res.company"].search(
            [
                ("l10n_pe_edi_send_invoice", "=", True),
                ("l10n_pe_edi_send_invoice_interval_unit", "!=", False),
                ("l10n_pe_edi_send_invoice_next_execution_date", "!=", False),
                (
                    "l10n_pe_edi_send_invoice_next_execution_date",
                    "<=",
                    fields.Datetime.now(),
                ),
            ]
        )
        for company_id in company_ids.filtered(lambda x: x.country_code == "PE"):
            company_id.l10n_pe_edi_send_invoice_next_execution_date = (
                company_id.l10n_pe_edi_send_invoice_next_execution_date
                + (
                    company_id.l10n_pe_edi_send_invoice_interval_unit == "hourly"
                    and relativedelta(hours=+1)
                    or relativedelta(days=+1)
                )
            )
            edi_requests = self.env["l10n_pe_edi.request"].search(
                [
                    ("ose_accepted", "=", False),
                    ("sunat_accepted", "=", False),
                    ("company_id", "=", company_id.id),
                    ("l10n_pe_edi_cron_send_count", ">", 1),
                ]
            )
            for edi_request in edi_requests:
                try:
                    edi_request.action_document_send()
                    if edi_request.ose_accepted:
                        edi_request.l10n_pe_edi_cron_send_count = 0
                    else:
                        edi_request.l10n_pe_edi_cron_send_count -= 1
                    self.env.cr.commit()
                except Exception:
                    self.env.cr.rollback()
                    edi_request.l10n_pe_edi_cron_send_count -= 1
                    self.env.cr.commit()

    def cron_check_documents(self):
        company_ids = self.env["res.company"].search(
            [("l10n_pe_edi_send_invoice", "=", True)]
        )
        for company_id in company_ids.filtered(lambda x: x.country_code == "PE"):
            edi_requests = self.env["l10n_pe_edi.request"].search(
                [
                    ("ose_accepted", "=", True),
                    ("sunat_accepted", "=", False),
                    ("company_id", "=", company_id.id),
                    ("l10n_pe_edi_cron_check_count", ">", 1),
                ]
            )
            # Change for new version --------------------------------------------------
            for edi_request_type in self._get_selection_document_type():
                edi_requests_by_type = edi_requests.filtered(
                    lambda x: x.l10n_pe_edi_document_type == edi_request_type[0]
                )
                for edi_request in edi_requests_by_type:
                    try:
                        edi_request.action_document_check()
                        if edi_request.sunat_accepted:
                            edi_request.l10n_pe_edi_cron_check_count = 0
                        else:
                            edi_request.l10n_pe_edi_cron_check_count -= 1
                        self.env.cr.commit()
                    except Exception:
                        self.env.cr.rollback()
                        edi_request.l10n_pe_edi_cron_check_count -= 1
                        self.env.cr.commit()


class EdiRequestLog(models.Model):
    _name = "l10n_pe_edi.request.log"
    _description = "EDI Request Log"
    _order = "date desc"

    request_id = fields.Many2one(
        comodel_name="l10n_pe_edi.request", string="EDI request"
    )
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    json_sent = fields.Text(string="JSON sent")
    json_response = fields.Text(string="JSON response")
    ose_accepted = fields.Boolean(string="Accepted by PSE/OSE")
    sunat_accepted = fields.Boolean(string="Accepted by SUNAT")
    sunat_canceled = fields.Boolean(string="Canceled by SUNAT")
    operation_type = fields.Char(string="Operation type")
    link_document = fields.Char(string="Document link")
    link_pdf = fields.Char(string="PDF link")
    link_xml = fields.Char(string="XML link")
    link_cdr = fields.Char(string="CDR link")
    response = fields.Text()
    sunat_description = fields.Char(string="SUNAT error description")
    sunat_note = fields.Char(string="SUNAT note")
    sunat_responsecode = fields.Char(string="SUNAT Response code")
    sunat_soap_error = fields.Char(string="SUNAT SOAP error")
