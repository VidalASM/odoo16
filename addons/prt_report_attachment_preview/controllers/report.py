###################################################################################
#
#    Copyright (C) 2020 Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import json
import re
from email.utils import encode_rfc2231

from werkzeug import urls

from odoo import http
from odoo.http import request
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.web.controllers.report import ReportController


class CxReportController(ReportController):
    def _get_extra_context_for_single_record(self, report_name, ignore_expr=None):
        """
        Get extra context values for single record report name
        evaluation. This is used to fill missing expressions with
        'report' string to avoid evaluation errors.

        Args:
        report_name (str): Name of the report.
            Example:
            "(object.state in ('draft', 'sent') and 'Quotation - %s' % (object.name))
            or 'Order - %s' % (object.name)"
        ignore_expr (list): List of expressions to ignore.

        Returns:
            Dict: Extra context values
        """
        ignore_expr = ignore_expr or []
        extra_ctx = {}
        for expr in re.findall(r"%.?\(.*?\)", report_name):
            # Remove percent sign and brackets, we don't need them
            expr = expr.replace("%", "").strip()[1:-1].strip()
            # If there is a dot in expression, then lets take
            # first part to get the variable name
            if "." in expr:
                expr = expr.split(".")[0]
            # Ignore expressions that are not variable names
            # (don't start with letter) or in ignore list
            if expr in ignore_expr or not expr[0].isaplha():
                continue
            extra_ctx[expr] = "report"
        return extra_ctx

    def _compose_report_file_name(self, docids, report):
        """Compose report file name.
        Uses report name + record name(s) if provided

        Args:
            docids ([Int]): list of record ids
            report (ir.action.report()): report record

        Returns:
            Char: composed name of the report
        """
        report_name = "report"
        if docids:
            records = request.env[report.model].browse(docids)
            record_count = len(docids)
            print_report_name = report.sudo().print_report_name
            if record_count == 1 and print_report_name:
                # Single record with formattable name
                extra_ctx = self._get_extra_context_for_single_record(
                    print_report_name,
                    ignore_expr=["object", "time"],
                )
                report_name = safe_eval(
                    print_report_name,
                    {
                        "object": records,
                        "time": time,
                        **extra_ctx,
                    },
                )
            else:
                # Multiple records
                # or single record report without formattable name
                report_name = (
                    f"{report.name} x{record_count}"
                    if record_count > 1
                    else report.name
                )
        else:
            report_name = report.name
        return report_name

    # ------------------------------------------------------
    # Report controllers
    # ------------------------------------------------------
    @http.route(
        [
            "/report/<converter>/<reportname>",
            "/report/<converter>/<reportname>/<docids>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter != "pdf":
            return super().report_routes(
                reportname, docids=docids, converter=converter, **data
            )

        report_obj = request.env["ir.actions.report"]
        report = report_obj._get_report_from_name(reportname)
        context = dict(request.env.context)

        # Options
        if data.get("options"):
            data_options = data.pop("options")
            data.update(json.loads(urls.url_unquote_plus(data_options)))

        # Context
        data_context = data.get("context")
        if data_context:
            context.update(json.loads(urls.url_unquote_plus(data_context)))

        # Set allowed companies if provided explicitly
        if data.get("cid"):
            allowed_company_ids = [int(i) for i in data.get("cid").split(",")]
            context.update(allowed_company_ids=allowed_company_ids)

        # Update request context
        request.env.context = context

        # Doc IDs
        if docids:
            docids = [int(i) for i in docids.split(",")]

            # Ensure user has access to the documents
            records = request.env[report.model].browse(docids)
            records.check_access_rule("read")

        report_file_name = self._compose_report_file_name(docids, report)
        pdf = report_obj.with_context(**context)._render_qweb_pdf(
            reportname, docids, data=data
        )[0]
        return request.make_response(
            pdf,
            headers=[
                ("Content-Type", "application/pdf"),
                ("Content-Length", len(pdf)),
                (
                    "Content-Disposition",
                    (
                        "inline; filename*=%s.pdf"
                        % encode_rfc2231(report_file_name, "utf-8")
                    ),
                ),
            ],
        )
