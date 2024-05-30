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
from collections import defaultdict

from odoo import fields, models


def group_by_doc_type(vals_list):
    res = defaultdict(list)
    for vals in vals_list:
        res[vals["l10n_pe_edi_document_type_id"]].append(vals)
    return res


class EdiDocumentType(models.Model):
    _name = "l10n_pe_edi.request.document.type"
    _description = "EDI Document Type"

    code = fields.Char(string="SUNAT Code")
    code_of = fields.Integer(string="Nubefact Code")
    name = fields.Char()
    active = fields.Boolean(default=True)

    kanban_dashboard = fields.Text(compute="_compute_kanban_dashboard")

    def _compute_kanban_dashboard(self):
        dashboard_data = self._get_edi_request_dashboard_data_batched()
        for rec in self:
            rec.kanban_dashboard = json.dumps(dashboard_data[rec.id])

    def _get_edi_request_dashboard_data_batched(self):
        self.env["l10n_pe_edi.request"].flush_model()
        dashboard_data = {}
        for rec in self:
            dashboard_data[rec.id] = {
                "company_count": len(self.env.companies),
            }
        self._fill_edi_request_dashboard_data(dashboard_data)
        return dashboard_data

    def _fill_edi_request_dashboard_data(self, dashboard_data):
        for rec in self:
            list_results_dict = self._list_results()
            count_results_dict = self._count_results(list_results_dict)
            dashboard_data[rec.id].update(count_results_dict[rec.id])

    def _count_results(self, list_results_dict):
        count_results = {}
        for rec in self:
            numbers = list_results_dict[rec.id]
            count_results[rec.id] = {
                "number_not_send": len(numbers["list_not_send"]),
                "number_not_ose": len(numbers["list_not_ose"]),
                "number_not_sunat": len(numbers["list_not_sunat"]),
            }
        return count_results

    def _list_results(self):
        field_list = [
            "l10n_pe_edi_request.l10n_pe_edi_document_type_id",
            "l10n_pe_edi_request.id",
            "l10n_pe_edi_request.state",
            "l10n_pe_edi_request.company_id",
        ]

        query, params = self._get_request_not_send_query().select(*field_list)
        self.env.cr.execute(query, params)
        query_results_not_send = group_by_doc_type(self.env.cr.dictfetchall())

        query, params = self._get_request_not_ose_query().select(*field_list)
        self.env.cr.execute(query, params)
        query_results_not_ose = group_by_doc_type(self.env.cr.dictfetchall())

        query, params = self._get_request_not_sunat_query().select(*field_list)
        self.env.cr.execute(query, params)
        query_results_not_sunat = group_by_doc_type(self.env.cr.dictfetchall())

        list_results = {}
        for rec in self:
            list_results[rec.id] = {
                "list_not_send": query_results_not_send[rec.id],
                "list_not_ose": query_results_not_ose[rec.id],
                "list_not_sunat": query_results_not_sunat[rec.id],
            }

        return list_results

    def _get_domain_not_send(self):
        return [
            ("state", "=", "draft"),
            ("ose_accepted", "=", False),
            ("sunat_accepted", "=", False),
            ("response", "=", False),
        ]

    def _get_domain_not_ose(self):
        return [
            ("state", "=", "draft"),
            ("ose_accepted", "=", False),
            ("sunat_accepted", "=", False),
            ("response", "!=", False),
        ]

    def _get_domain_not_sunat(self):
        return [
            ("state", "=", "sent"),
            ("ose_accepted", "=", True),
            ("sunat_accepted", "=", False),
        ]

    def _get_request_not_send_query(self):
        domain = self._get_domain_not_send()
        return self.env["l10n_pe_edi.request"]._where_calc(domain)

    def _get_request_not_ose_query(self):
        domain = self._get_domain_not_ose()
        return self.env["l10n_pe_edi.request"]._where_calc(domain)

    def _get_request_not_sunat_query(self):
        domain = self._get_domain_not_sunat()
        return self.env["l10n_pe_edi.request"]._where_calc(domain)

    def get_request_action_doc_type(self):
        domain = [("l10n_pe_edi_document_type_id", "=", self.id)]
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "l10n_pe_edi_base.l10n_pe_edi_request_invoice_action"
        )
        action["context"] = {}
        action["domain"] = domain
        return action

    def get_request_not_send_action(self):
        action = self.get_request_action_doc_type()
        action["domain"] += self._get_domain_not_send()
        return action

    def get_request_not_ose_action(self):
        action = self.get_request_action_doc_type()
        action["domain"] += self._get_domain_not_ose()
        return action

    def get_request_not_sunat_action(self):
        action = self.get_request_action_doc_type()
        action["domain"] += self._get_domain_not_sunat()
        return action
