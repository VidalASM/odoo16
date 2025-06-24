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
import logging
import os

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning(
        "The num2words python library is not installed, amount-to-text features won't "
        "be fully available."
    )
    num2words = None

CURRENCY = {
    "PEN": 1,
    "USD": 2,
    "EUR": 3,
    "GBP": 4,
}


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_latam_document_type_id = fields.Many2one(
        'l10n_latam.document.type', string='Document Type', readonly=False, #auto_join=True, index='btree_not_null',
        # states={'posted': [('readonly', True)]}, 
        # compute='_compute_l10n_latam_document_type', inverse='_inverse_latam_document_type', store=True
        )

    # ==== Business fields ====
    l10n_pe_edi_shop_id = fields.Many2one(
        comodel_name="l10n_pe_edi.shop",
        string="Shop",
        related="journal_id.l10n_pe_edi_shop_id",
        store=True,
    )
    l10n_pe_edi_is_einvoice = fields.Boolean(
        string="Is E-invoice", related="journal_id.l10n_pe_edi_is_einvoice", store=True
    )
    l10n_pe_edi_request_id = fields.Many2one(
        comodel_name="l10n_pe_edi.request", string="PSE/OSE request", copy=False
    )
    l10n_pe_edi_response = fields.Text(
        string="Response", related="l10n_pe_edi_request_id.response", store=True
    )
    l10n_pe_edi_ose_accepted = fields.Boolean(
        related="l10n_pe_edi_request_id.ose_accepted"
    )
    l10n_pe_edi_sunat_accepted = fields.Boolean(
        related="l10n_pe_edi_request_id.sunat_accepted"
    )
    # Cambiado desde 'l10n_pe_edi_operation_type' porque el campo ya existe en Enterprise v16
    l10n_pe_edi_odoofact_operation_type = fields.Selection(
        selection=[
            ("1", _("INTERNAL SALE")),
            ("2", _("EXPORTATION")),
            ("4", _("INTERNAL SALE - ADVANCES")),
            ("29", _("NON-DOMICILED SALES THAT DO NOT QUALIFY AS EXPORTS")),
            ("30", _("OPERATION SUBJECT TO DETRACTION")),
            ("33", _("DETRACTION - CARGO TRANSPORTATION SERVICES")),
            ("34", _("OPERATION SUBJECT TO PERCEPTION")),
            ("32", _("DETRACTION - PASSENGER TRANSPORTATION SERVICES")),
            ("31", _("DETRACTION - HYDROBIOLOGICAL RESOURCES")),
        ],
        string="Transaction type",
        copy=False,
        states={"draft": [("readonly", False)]},
        help="Default 1, the others are for very special types of operations, do not "
        "hesitate to consult with us for more information",
        default="1",
    )
    l10n_pe_edi_exchange_rate = fields.Float(
        string="Exchange Rate",
        digits=(12, 3),
        compute="_compute_l10n_pe_edi_exchange_rate",
        tracking=True,
    )
    l10n_pe_edi_picking_number_ids = fields.One2many(
        comodel_name="l10n_pe_edi.picking.number",
        inverse_name="invoice_id",
        copy=False,
        string="Reference Guides",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    l10n_pe_edi_is_sale_credit = fields.Boolean(
        string="Sale on Credit",
        compute="_compute_l10n_pe_edi_is_sale_credit",
        store=True,
        tracking=True,
    )
    l10n_pe_edi_dues_ids = fields.One2many(
        comodel_name="l10n_pe_edi.dues",
        inverse_name="move_id",
        string="Dues",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    l10n_pe_edi_service_order = fields.Char(
        string="Purchase/Service Order",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    l10n_pe_edi_reversal_type_id = fields.Many2one(
        comodel_name="l10n_pe_edi.catalog.09",
        string="Credit note type",
        help="Catalog 09: Types of Credit note",
    )
    l10n_pe_edi_debit_type_id = fields.Many2one(
        comodel_name="l10n_pe_edi.catalog.10",
        string="Debit note type",
        help="Catalog 10: Types of Debit note",
    )
    l10n_pe_edi_origin_move_id = fields.Many2one(
        comodel_name="account.move",
        string="Origin Move",
        compute="_compute_origin_move",
        store=True,
    )
    l10n_pe_edi_cancel_reason = fields.Char(string="Cancel Reason", copy=False)
    l10n_pe_edi_sunat_canceled_progress = fields.Boolean(
        string="Cancellation is in progress", copy=False, default=False
    )
    l10n_pe_edi_retention_type_id = fields.Many2one(
        comodel_name="l10n_pe_edi.catalog.23", string="Retention Type", copy=False
    )
    l10n_pe_edi_detraction_type_id = fields.Many2one(
        comodel_name="l10n_pe_edi.catalog.54", string="Detraction Type", copy=False
    )
    l10n_pe_edi_detraction_payment_type_id = fields.Many2one(
        comodel_name="l10n_pe_edi.catalog.59",
        string="Detraction Payment Type",
        copy=False,
    )

    # === Amount fields ===
    l10n_pe_edi_amount_base = fields.Monetary(
        string="Base Amount", compute="_compute_l10n_pe_edi_amount_base", tracking=True
    )
    l10n_pe_edi_amount_free = fields.Monetary(
        string="Free Amount",
        compute="_compute_l10n_pe_edi_tax_totals",
        tracking=True,
    )
    l10n_pe_edi_amount_exonerated = fields.Monetary(
        string="Exonerated Amount",
        compute="_compute_l10n_pe_edi_tax_totals",
        tracking=True,
    )
    l10n_pe_edi_amount_unaffected = fields.Monetary(
        string="Unaffected Amount",
        compute="_compute_l10n_pe_edi_tax_totals",
        tracking=True,
    )
    l10n_pe_edi_global_discount = fields.Monetary(
        string="Global Discount Amount",
        compute="_compute_l10n_pe_edi_discounts",
        tracking=True,
    )
    l10n_pe_edi_amount_discount = fields.Monetary(
        string="Total Discount Amount",
        compute="_compute_l10n_pe_edi_discounts",
        tracking=True,
    )
    l10n_pe_edi_amount_advance = fields.Monetary(
        string="Total Advance Amount",
        compute="_compute_l10n_pe_edi_discounts",
        tracking=True,
    )
    l10n_pe_edi_total_retention = fields.Monetary(
        string="Total Retention",
        store=True,
        compute="_compute_total_retention",
        tracking=True,
    )
    l10n_pe_edi_total_detraction = fields.Monetary(
        string="Total Detraction",
        store=True,
        compute="_compute_total_detraction",
        tracking=True,
    )
    l10n_pe_edi_total_detraction_signed = fields.Monetary(
        string="Total Detraction Signed",
        store=True,
        compute="_compute_total_detraction",
        currency_field="company_currency_id",
        tracking=True,
    )

    # ==== Tax fields ====
    l10n_pe_edi_igv_percent = fields.Float(
        string="Percentage IGV", compute="_compute_l10n_pe_edi_igv_percent"
    )
    l10n_pe_edi_amount_igv = fields.Monetary(
        string="IGV Amount", compute="_compute_l10n_pe_edi_tax_totals", tracking=True
    )
    l10n_pe_edi_amount_icbper = fields.Monetary(
        string="ICBPER Amount",
        compute="_compute_l10n_pe_edi_tax_totals",
        tracking=True,
    )

    @api.onchange("l10n_latam_available_document_type_ids")
    def _onchange_l10n_latam_available_document_type_ids(self):
        if self.l10n_latam_available_document_type_ids:
            self.l10n_latam_document_type_id = self.l10n_latam_available_document_type_ids[0].id

    @api.onchange("l10n_pe_edi_odoofact_operation_type")
    def _onchange_l10n_pe_edi_odoofact_operation_type(self):
        fiscal_pos_exp = self.env["account.fiscal.position"].search(
            [("name", "ilike", "expor")], limit=1
        )
        if self.l10n_pe_edi_odoofact_operation_type in ["2", "3"] and fiscal_pos_exp:
            self.fiscal_position_id = fiscal_pos_exp.id
        else:
            self._compute_fiscal_position_id()

    @api.onchange("l10n_pe_edi_detraction_type_id")
    def _onchange_l10n_pe_edi_detraction_type_id(self):
        company_id = self.env.company
        self.l10n_pe_edi_detraction_payment_type_id = (
            self.l10n_pe_edi_detraction_type_id
            and company_id.l10n_pe_edi_detraction_payment_type_id
            and company_id.l10n_pe_edi_detraction_payment_type_id.id
            or False
        )
        self.l10n_pe_edi_odoofact_operation_type = (
            self.l10n_pe_edi_detraction_type_id and "30" or "1"
        )

    @api.depends("l10n_pe_edi_retention_type_id", "amount_total")
    def _compute_total_retention(self):
        for move in self:
            move.l10n_pe_edi_total_retention = (
                move.l10n_pe_edi_retention_type_id
                and (
                    move.amount_total * (move.l10n_pe_edi_retention_type_id.rate / 100)
                )
                or 0.0
            )

    @api.depends(
        "l10n_pe_edi_detraction_type_id",
        "l10n_pe_edi_detraction_type_id.rate",
        "amount_total",
        "amount_total_signed",
    )
    def _compute_total_detraction(self):
        for move in self:
            move.l10n_pe_edi_total_detraction = (
                move.l10n_pe_edi_detraction_type_id
                and round(
                    move.amount_total
                    * (move.l10n_pe_edi_detraction_type_id.rate / 100),
                    0,
                )
                or 0.0
            )
            detraction_signed = move.l10n_pe_edi_total_detraction
            if move.currency_id != move.company_id.currency_id:
                detraction_signed = move.currency_id._convert(
                    detraction_signed,
                    move.company_id.currency_id,
                    move.company_id,
                    move.date or fields.Date.context_today(move),
                )
            move.l10n_pe_edi_total_detraction_signed = round(detraction_signed, 0)

    @api.depends("date", "company_id", "currency_id")
    def _compute_l10n_pe_edi_exchange_rate(self):
        for move in self:
            currency_rate = self.env["res.currency"]._get_conversion_rate(
                from_currency=move.company_currency_id,
                to_currency=move.currency_id,
                company=move.company_id,
                date=move.date or fields.Date.context_today(move),
            )
            move.l10n_pe_edi_exchange_rate = 1 / currency_rate

    @api.depends("invoice_date", "invoice_date_due", "invoice_payment_term_id")
    def _compute_l10n_pe_edi_is_sale_credit(self):
        for move in self:
            if move.l10n_latam_document_type_id.code == "01":
                if any(
                    line.date_maturity
                    and line.date_maturity
                    > (move.invoice_date or fields.Date.context_today(move))
                    for line in move.line_ids.filtered(
                        lambda x: x.display_type == "payment_term"
                    )
                ):
                    move.l10n_pe_edi_is_sale_credit = True
                    continue
            move.l10n_pe_edi_is_sale_credit = False

    @api.depends("reversed_entry_id", "debit_origin_id")
    def _compute_origin_move(self):
        for rec in self:
            rec.l10n_pe_edi_origin_move_id = (
                rec.debit_origin_id or rec.reversed_entry_id
            )

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            move.fill_l10n_pe_edi_is_sale_credit()
        return moves

    def _get_fields_to_compute_dues(self):
        return [
            "invoice_date",
            "invoice_date_due",
            "invoice_payment_term_id",
            "l10n_pe_edi_retention_type_id",
            "l10n_pe_edi_detraction_type_id",
        ]

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for rec in self:
            if any(v in self._get_fields_to_compute_dues() for v in vals):
                rec.fill_l10n_pe_edi_is_sale_credit()
        return res

    def _get_dues_lines(self):
        dues = []
        for index, line in enumerate(
            self.line_ids.filtered(lambda x: x.display_type == "payment_term").sorted(
                "date_maturity"
            )
        ):
            dues.append(
                {
                    "dues_number": index + 1,
                    "paid_date": line.date_maturity,
                    "amount": abs(line.amount_currency),
                },
            )
        for due in dues:
            amount_discount = (
                self.l10n_pe_edi_retention_type_id
                and self.l10n_pe_edi_total_retention
                or self.l10n_pe_edi_detraction_type_id
                and self.l10n_pe_edi_total_detraction
                or 0.0
            ) / len(dues)
            due.update({"amount": due["amount"] - amount_discount})
        return dues

    def fill_l10n_pe_edi_is_sale_credit(self):
        dues = [(5, 0, 0)]
        if self.l10n_pe_edi_is_sale_credit:
            for due in self._get_dues_lines():
                dues.append((0, 0, due))
        self.write({"l10n_pe_edi_dues_ids": dues})

    @api.depends("invoice_line_ids", "invoice_line_ids.tax_ids")
    def _compute_l10n_pe_edi_igv_percent(self):
        self.l10n_pe_edi_igv_percent = 0.0
        for rec in self:
            invoice_lines = self.invoice_line_ids.filtered(
                lambda x: x.display_type == "product" and x.tax_ids
            )
            if not invoice_lines:
                continue
            igv_tax = invoice_lines[0].tax_ids.filtered(
                lambda x: x.tax_group_id.name == "IGV"
            )
            if not igv_tax:
                rec.l10n_pe_edi_igv_percent = 18.0
            else:
                rec.l10n_pe_edi_igv_percent = igv_tax[0].amount

    @api.depends(
        "line_ids",
        "line_ids.display_type",
        "line_ids.tax_ids",
        "line_ids.tax_group_id",
        "line_ids.l10n_pe_edi_amount_free",
    )
    def _compute_l10n_pe_edi_tax_totals(self):
        for move in self:
            sign = move.direction_sign
            amount_free = 0.0
            amount_exonerated = 0.0
            amount_unaffected = 0.0
            amount_igv = 0.0
            amount_isc = 0.0
            amount_icbper = 0.0

            for line in move.line_ids.filtered(lambda x: x.display_type == "product"):
                if move.is_invoice(True):
                    if any(
                        tax.l10n_pe_edi_tax_code in ["9996"] for tax in line.tax_ids
                    ):
                        amount_free += line.l10n_pe_edi_amount_free
                    elif any(
                        tax.l10n_pe_edi_tax_code in ["9997"] for tax in line.tax_ids
                    ):
                        amount_exonerated += line.price_subtotal
                    elif any(
                        tax.l10n_pe_edi_tax_code in ["9998"] for tax in line.tax_ids
                    ):
                        amount_unaffected += line.price_subtotal

            for line in move.line_ids.filtered(lambda x: x.display_type == "tax"):
                if move.is_invoice(True):
                    if line.tax_group_id.name == "IGV":
                        amount_igv += line.amount_currency
                    if line.tax_group_id.name == "ISC":
                        amount_isc += line.amount_currency
                    if line.tax_group_id.name == "ICBPER":
                        amount_icbper += line.amount_currency

            move.l10n_pe_edi_amount_free = amount_free
            move.l10n_pe_edi_amount_exonerated = amount_exonerated
            move.l10n_pe_edi_amount_unaffected = amount_unaffected

            move.l10n_pe_edi_amount_igv = sign * amount_igv
            # move.l10n_pe_edi_amount_isc = sign * amount_isc
            move.l10n_pe_edi_amount_icbper = sign * amount_icbper

    @api.depends("line_ids", "line_ids.quantity", "line_ids.discount")
    def _compute_l10n_pe_edi_discounts(self):
        for move in self:
            advance_discount = 0.0
            global_discount = 0.0
            total_discount = 0.0
            for line in move.line_ids.filtered(lambda x: x.display_type == "product"):
                if line.price_unit < 0.0 and move.move_type == 'out_invoice': 
                    global_discount += abs(
                            line.l10n_pe_edi_price_unit_excluded * line.quantity
                        )
                elif line.quantity < 0.0 and getattr(line, "is_downpayment", False):
                    advance_discount += abs(
                        line.l10n_pe_edi_price_unit_excluded * line.quantity
                    )
                elif line.discount > 0.0 and not line.l10n_pe_edi_free_product:
                    total_discount += (
                        line.l10n_pe_edi_price_unit_excluded
                        * (line.discount / 100.0)
                        * line.quantity
                    )
            move.l10n_pe_edi_amount_advance = advance_discount
            move.l10n_pe_edi_global_discount = global_discount
            move.l10n_pe_edi_amount_discount = total_discount + global_discount

    @api.depends(
        "amount_untaxed",
        "l10n_pe_edi_amount_exonerated",
        "l10n_pe_edi_amount_unaffected",
    )
    def _compute_l10n_pe_edi_amount_base(self):
        for move in self:
            move.l10n_pe_edi_amount_base = move.amount_untaxed
            if (
                move.l10n_pe_edi_amount_exonerated > 0.0
                or move.l10n_pe_edi_amount_unaffected > 0.0
            ):
                move.l10n_pe_edi_amount_base = 0.0

    def _get_default_detraction(self):
        detraction = False
        detractions = self.invoice_line_ids.mapped(
            "product_id.l10n_pe_edi_detraction_type_id"
        )
        if detractions:
            detraction = detractions.sorted("rate", reverse=True)
            detraction = detraction[0]
        return detraction

    def _set_default_detraction(self):
        detraction = self._get_default_detraction()
        self.l10n_pe_edi_detraction_type_id = detraction and detraction.id or False
        self._onchange_l10n_pe_edi_detraction_type_id()

    def auto_applies_before_posting(self):
        for rec in self:
            if (
                rec.l10n_pe_edi_is_einvoice
                and rec._get_default_detraction()
                and rec.amount_total_signed
                >= rec.company_id.l10n_pe_edi_min_amount_detraction
                and not rec.l10n_pe_edi_detraction_type_id
            ):
                rec._set_default_detraction()

    def action_post(self):
        self.auto_applies_before_posting()
        res = super(AccountMove, self).action_post()
        for move in self:
            if (
                move.l10n_pe_edi_is_einvoice
                and move.l10n_pe_edi_shop_id
                and not move.l10n_pe_edi_request_id
            ):
                document_type = self.env["l10n_pe_edi.request.document.type"].search(
                    [("code", "=", move.l10n_latam_document_type_id.code)], limit=1
                )
                request_id = self.env["l10n_pe_edi.request"].create(
                    {
                        "company_id": move.company_id.id,
                        "l10n_pe_edi_shop_id": move.l10n_pe_edi_shop_id
                        and move.l10n_pe_edi_shop_id.id
                        or False,
                        "l10n_pe_edi_document_type": move.l10n_latam_document_type_id
                        and move.l10n_latam_document_type_id.code
                        or False,
                        "l10n_pe_edi_document_type_id": document_type
                        and document_type.id
                        or False,
                        "document_number": move.name,
                        "document_date": move.invoice_date,
                        "model": move._name,
                        "res_id": move.id,
                    }
                )
                move.l10n_pe_edi_request_id = request_id.id
        return res

    @api.depends("company_id", "invoice_filter_type_domain")
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = m.invoice_filter_type_domain or "general"
            company_id = m.company_id.id or self.env.company.id
            domain = [("company_id", "=", company_id), ("type", "=", journal_type)]
            if m.move_type == "out_invoice":
                domain.append(
                    ("l10n_latam_document_type_id.code", "in", ["01", "03", "08"])
                )
            if m.move_type == "out_refund":
                domain.append(("l10n_latam_document_type_id.code", "in", ["07"]))
            m.suitable_journal_ids = self.env["account.journal"].search(domain)

    def _search_default_journal(self):
        if self.move_type == "out_refund":
            journal_type = self.invoice_filter_type_domain or "general"
            company_id = self.company_id.id or self.env.company.id
            domain = [
                ("company_id", "=", company_id),
                ("type", "=", journal_type),
                ("l10n_latam_document_type_id.code", "in", ["07"]),
            ]
            return self.env["account.journal"].search(domain, limit=1)
        return super(AccountMove, self)._search_default_journal()

    @api.onchange("l10n_latam_document_type_id", "l10n_latam_document_number")
    def _inverse_l10n_latam_document_number(self):
        pass

    @api.depends("move_type", "journal_id", "l10n_latam_available_document_type_ids")
    def _compute_l10n_latam_document_type(self):
        document_types = self.env['l10n_latam.document.type'].search([])
        for move in self.filtered(lambda x: x.state == "draft"):
            if move.journal_id and move.journal_id.l10n_latam_document_type_id:
                move.l10n_latam_document_type_id = (
                    move.journal_id.l10n_latam_document_type_id
                )
            elif move.l10n_latam_available_document_type_ids:
                # move.l10n_latam_document_type_id = document_types #and document_types[0].id
                move.l10n_latam_document_type_id = move.l10n_latam_available_document_type_ids[0].id
    
    @api.depends("move_type", "journal_id", "l10n_latam_available_document_type_ids", "l10n_latam_document_type_id")
    def _inverse_latam_document_type(self):
        print("-------------inverse-------------------")

    def _l10n_pe_edi_get_formatted_sequence(self, number=0):
        return "%s-%06d" % (self.journal_id.code, number)

    def _get_starting_sequence(self):
        if self.l10n_pe_edi_is_einvoice:
            if self.l10n_latam_document_type_id and self.journal_id.code:
                return self._l10n_pe_edi_get_formatted_sequence()
        return super()._get_starting_sequence()

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super(AccountMove, self)._get_last_sequence_domain(
            relaxed
        )
        if self.l10n_pe_edi_is_einvoice:
            param.update(
                {
                    "anti_regex": "^(?:.*?)(?:((?<=\\\\D)|(?<=^))((19|20|21)?\\\\d{2}))(?:\\\\D+?)$",
                }
            )
        return where_string, param

    def action_invoice_sent(self):
        """Open a window to compose an email, with the edi invoice template
        message loaded by default
        """
        res = super(AccountMove, self).action_invoice_sent()
        template = self.env.ref(
            "l10n_pe_edi_odoofact.email_template_edi_invoice", raise_if_not_found=False
        )
        if template:
            res["context"].update(
                {"default_template_id": template and template.id or False}
            )
        return res

    @api.model
    def _deduce_sequence_number_reset(self, name):
        if self.env.company.country_id.code == "PE" and self.move_type not in (
            "entry",
            "in_invoice",
            "in_refund",
            "in_receipt",
        ):
            return "never"
        return super(AccountMove, self)._deduce_sequence_number_reset(name)

    def action_document_send(self):
        """
        This method creates the request to PSE/OSE provider
        """
        for rec in self.filtered(
            lambda x: x.state == "posted"
            and x.l10n_pe_edi_is_einvoice
            and not x.l10n_pe_edi_ose_accepted
        ):
            rec.l10n_pe_edi_request_id.action_api_connect("generar")
            if (
                rec.l10n_pe_edi_request_id.log_id
                and rec.l10n_pe_edi_request_id.log_id.json_response
            ):
                json_response = json.loads(
                    rec.l10n_pe_edi_request_id.log_id.json_response
                )
                if json_response.get("codigo", 0) == 23:
                    rec.l10n_pe_edi_request_id.action_api_connect("consultar")

    def action_document_check(self):
        """
        Send the request for Checking document status for electronic invoices
        """
        for rec in self.filtered(
            lambda x: x.state == "posted"
            and x.l10n_pe_edi_is_einvoice
            and x.l10n_pe_edi_ose_accepted
            and (
                not x.l10n_pe_edi_sunat_accepted
                or x.l10n_pe_edi_sunat_canceled_progress
            )
        ):
            rec.l10n_pe_edi_request_id.action_api_connect("consultar")
            if rec.l10n_pe_edi_request_id.sunat_canceled:
                rec.l10n_pe_edi_sunat_canceled_progress = False
                rec.button_draft()
                rec.button_cancel()

    def action_document_cancel(self):
        """
        Cancel the invoice and send the cancelation request for electronic invoice
        """
        for rec in self.filtered(
            lambda x: x.state == "posted"
            and x.l10n_pe_edi_is_einvoice
            and x.l10n_pe_edi_ose_accepted
            and x.l10n_pe_edi_sunat_accepted
        ):
            rec.l10n_pe_edi_request_id.action_api_connect("anular")
            rec.l10n_pe_edi_sunat_canceled_progress = True

    def _get_include_downpayment(self):
        return any(
            getattr(line, "is_downpayment", False) for line in self.invoice_line_ids
        )

    def _get_fill_downpayment(self):
        return any(
            not line.l10n_pe_edi_advance_serie or line.l10n_pe_edi_advance_number == 0
            for line in self.invoice_line_ids.filtered(
                lambda x: getattr(x, "is_downpayment", False) and x.quantity < 0.0
            )
        )

    def check_data_to_send(self):
        if not self.l10n_latam_document_type_id.type_of:
            raise UserError(
                _("The code of document type for the odoofact must be entered")
            )
        if not self.l10n_pe_edi_odoofact_operation_type:
            raise UserError(_("The Transaction Type must be entered"))
        if not self.commercial_partner_id:
            raise UserError(
                _(
                    "The partner must be entered, if the sale does not have a partner"
                    ", you must create one with the type of identity document '-' and "
                    "the document number '00000000'"
                )
            )
        if not self.commercial_partner_id.l10n_latam_identification_type_id:
            raise UserError(
                _("The type of identity document of the partner must be entered")
            )
        if not self.commercial_partner_id.vat:
            raise UserError(_("The document number of the partner must be entered"))

        if not CURRENCY.get(self.currency_id.name, False):
            raise UserError(
                _(
                    "Currency '%(code)s, %(name)s' is not available for Electronic "
                    "invoice. Contact to the Administrator."
                )
                % (self.currency_id.name, self.currency_id.currency_unit_label)
            )
        if self._get_include_downpayment():
            if self.l10n_pe_edi_odoofact_operation_type != "4":
                raise UserError(
                    _(
                        "The document includes advances, you must use the transaction "
                        "type 'INTERNAL SALE - ADVANCES'"
                    )
                )
            if self._get_fill_downpayment():
                raise UserError(
                    _(
                        "The document includes advances, you must enter the document "
                        "related to the advance on the corresponding line"
                    )
                )

        self.check_data_to_send_extend()

    def check_data_to_send_extend(self):
        if self.l10n_pe_edi_retention_type_id and self.l10n_pe_edi_detraction_type_id:
            raise UserError(
                _(
                    "Retention and Detraction cannot be applied at the same time "
                    "since they are completely different operations."
                )
            )

        if self.l10n_pe_edi_retention_type_id:
            if self.l10n_latam_document_type_id.type_of != "1":
                raise UserError(_("The retention can only be applied to invoices."))
            if (
                self.amount_total_signed
                <= self.company_id.l10n_pe_edi_min_amount_retention
            ):
                raise UserError(
                    _(
                        "The retention can only be applied for amounts greater "
                        "than S/. %s"
                    )
                    % (str(self.company_id.l10n_pe_edi_min_amount_retention))
                )

        if self.l10n_pe_edi_detraction_type_id:
            if self.l10n_latam_document_type_id.type_of != "1":
                raise UserError(_("The detraction can only be applied to invoices."))
            if self.l10n_pe_edi_odoofact_operation_type not in ["30", "31", "32", "33"]:
                raise UserError(
                    _(
                        "Invoice with detraction, the type of operation must be detraction."
                    )
                )
        elif self._get_detraction_type_of_lines():
            raise UserError(
                _("Detraction is mandatory for amounts greater than S/. %s")
                % (str(self.company_id.l10n_pe_edi_min_amount_detraction))
            )

    def _get_partner_address_odoofact(self, partner):
        if not partner:
            return ""
        return (
            (partner.street or "")
            + (partner.l10n_pe_district and ", " + partner.l10n_pe_district.name or "")
            + (partner.city_id and ", " + partner.city_id.name or "")
            + (partner.state_id and ", " + partner.state_id.name or "")
            + (partner.country_id and ", " + partner.country_id.name or "")
        )

    def _get_document_values_generar_odoofact(self, ose_supplier):
        commercial = self.commercial_partner_id
        commercial_doc_type = commercial.l10n_latam_identification_type_id
        currency = CURRENCY.get(self.currency_id.name, False)
        return {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": self.l10n_latam_document_type_id.type_of,
            "serie": str(self.sequence_prefix)[0:4],
            "numero": self.sequence_number,
            "sunat_transaction": int(self.l10n_pe_edi_odoofact_operation_type),
            "cliente_tipo_de_documento": commercial_doc_type.l10n_pe_vat_code,
            "cliente_numero_de_documento": self.commercial_partner_id.vat,
            "cliente_denominacion": self.commercial_partner_id.name,
            "cliente_direccion": self._get_partner_address_odoofact(self.partner_id),
            "cliente_email": self.partner_id.email and self.partner_id.email or "",
            "fecha_de_emision": self.invoice_date.strftime("%d-%m-%Y"),
            "fecha_de_vencimiento": self.invoice_date_due
            and self.invoice_date_due.strftime("%d-%m-%Y")
            or "",
            "moneda": currency,
            "tipo_de_cambio": self.l10n_pe_edi_exchange_rate,
            "porcentaje_de_igv": self.l10n_pe_edi_igv_percent,
            "descuento_global": self.l10n_pe_edi_global_discount,
            "total_descuento": self.l10n_pe_edi_amount_discount,
            "total_anticipo": self.l10n_pe_edi_amount_advance,
            "total_gravada": self.l10n_pe_edi_amount_base,
            "total_inafecta": self.l10n_pe_edi_amount_unaffected,
            "total_exonerada": self.l10n_pe_edi_amount_exonerated,
            "total_igv": self.l10n_pe_edi_amount_igv,
            "total_gratuita": self.l10n_pe_edi_amount_free,
            "total_otros_cargos": 0.0,  # ---------
            "total_isc": 0.0,  # ---------
            "total": self.amount_total,
            "retencion_tipo": self.l10n_pe_edi_retention_type_id
            and int(self.l10n_pe_edi_retention_type_id.code)
            or "",
            "retencion_base_imponible": self.l10n_pe_edi_retention_type_id
            and abs(self.amount_total)
            or "",
            "total_retencion": self.l10n_pe_edi_retention_type_id
            and abs(self.l10n_pe_edi_total_retention)
            or "",
            "total_impuestos_bolsas": self.l10n_pe_edi_amount_icbper,
            "observaciones": self.narration or "",
            "documento_que_se_modifica_tipo": self.l10n_pe_edi_origin_move_id
            and (self.l10n_pe_edi_origin_move_id.name[0] == "F" and 1 or 2)
            or "",
            "documento_que_se_modifica_serie": self.l10n_pe_edi_origin_move_id
            and str(self.l10n_pe_edi_origin_move_id.sequence_prefix)[0:4]
            or "",
            "documento_que_se_modifica_numero": self.l10n_pe_edi_origin_move_id
            and self.l10n_pe_edi_origin_move_id.sequence_number
            or "",
            "tipo_de_nota_de_credito": self.l10n_pe_edi_reversal_type_id
            and int(self.l10n_pe_edi_reversal_type_id.code_of)
            or "",
            "tipo_de_nota_de_debito": self.l10n_pe_edi_debit_type_id
            and int(self.l10n_pe_edi_debit_type_id.code_of)
            or "",
            "enviar_automaticamente_a_la_sunat": "",  # ---------
            "enviar_automaticamente_al_cliente": self.l10n_pe_edi_shop_id.send_email
            and "true"
            or "false",
            "codigo_unico": "%s|%s|%s-%s"
            % (
                "odoo",
                self.company_id.partner_id.vat,
                str(self.sequence_prefix)[0:4],
                str(self.sequence_number),
            ),
            "condiciones_de_pago": self.invoice_payment_term_id
            and self.invoice_payment_term_id.name
            or "",
            "medio_de_pago": self.l10n_pe_edi_is_sale_credit
            and "venta_al_credito"
            or "contado",
            "orden_compra_servicio": self.l10n_pe_edi_service_order or "",
            "detraccion": self.l10n_pe_edi_detraction_type_id and "true" or "false",
            "detraccion_tipo": self.l10n_pe_edi_detraction_type_id
            and int(self.l10n_pe_edi_detraction_type_id.code_of)
            or "",
            "detraccion_total": self.l10n_pe_edi_detraction_type_id
            and self.l10n_pe_edi_total_detraction_signed
            or "",
            "detraccion_porcentaje": self.l10n_pe_edi_detraction_type_id
            and self.l10n_pe_edi_detraction_type_id.rate
            or "",
            "medio_de_pago_detraccion": self.l10n_pe_edi_detraction_type_id
            and self.l10n_pe_edi_detraction_payment_type_id
            and int(self.l10n_pe_edi_detraction_payment_type_id.code_of)
            or "",
            "generado_por_contingencia": self.journal_id.l10n_pe_edi_contingency
            and "true"
            or "false",
            "items": getattr(self, "_get_lines_values_generar_%s" % (ose_supplier))(),
            "guias": getattr(self, "_get_guides_values_generar_%s" % (ose_supplier))(),
            "venta_al_credito": getattr(
                self, "_get_dues_values_generar_%s" % (ose_supplier)
            )(),
        }

    def _get_lines_values_generar_odoofact(self):
        lines = []
        for line in self.invoice_line_ids.filtered(
            lambda x: x.display_type == "product"
            and x.price_unit > 0.0
            and (not x.quantity < 0.0 or getattr(x, "is_downpayment", False))
        ):
            product_uom_code = (
                line.product_uom_id
                and (
                    line.product_uom_id.l10n_pe_edi_uom_code_id
                    and line.product_uom_id.l10n_pe_edi_uom_code_id.code
                    or False
                )
                or (
                    line.product_id
                    and (line.product_id.type != "service" and "NIU" or "ZZ")
                    or "ZZ"
                )
            )
            lines.append(
                {
                    "unidad_de_medida": product_uom_code,
                    "codigo": line.product_id and line.product_id.default_code or "",
                    "descripcion": self._get_description_without_product_code(
                        line.product_id, line.name
                    ),
                    "cantidad": abs(line.quantity),
                    "valor_unitario": abs(line.l10n_pe_edi_price_unit_excluded),
                    "precio_unitario": abs(line.l10n_pe_edi_price_unit_included),
                    "descuento": abs(line.l10n_pe_edi_amount_discount),
                    "subtotal": line.l10n_pe_edi_free_product
                    and line.l10n_pe_edi_amount_free
                    or line.price_subtotal,
                    "tipo_de_igv": line.l10n_pe_edi_tax_type.code_of,
                    "tipo_de_ivap": "",
                    "igv": abs(line.l10n_pe_edi_igv_amount),
                    "impuesto_bolsas": abs(line.l10n_pe_edi_icbper_amount),
                    "total": line.l10n_pe_edi_free_product
                    and abs(line.l10n_pe_edi_amount_free)
                    or abs(line.price_total),
                    "anticipo_regularizacion": line.quantity < 0.0
                    and getattr(line, "is_downpayment", False)
                    and "true"
                    or "false",
                    "anticipo_documento_serie": line.l10n_pe_edi_advance_serie
                    and line.l10n_pe_edi_advance_serie
                    or "",
                    "anticipo_documento_numero": line.l10n_pe_edi_advance_number or "",
                    "codigo_producto_sunat": line.product_id.l10n_pe_edi_product_code_id
                    and line.product_id.l10n_pe_edi_product_code_id.code
                    or "",
                    "tipo_de_isc": "",  # ---------
                    "isc": "",  # ---------
                }
            )
        return lines

    def _get_guides_values_generar_odoofact(self):
        guide_list = []
        for guide in self.l10n_pe_edi_picking_number_ids:
            guide_list.append(
                {
                    "guia_tipo": guide.type or "",
                    "guia_serie_numero": guide.name or "",
                }
            )
        return guide_list

    def _get_dues_values_generar_odoofact(self):
        dues_list = []
        if self.l10n_pe_edi_is_sale_credit:
            for due in self.l10n_pe_edi_dues_ids:
                dues_list.append(
                    {
                        "cuota": due.dues_number,
                        "fecha_de_pago": due.paid_date.strftime("%d-%m-%Y"),
                        "importe": due.amount,
                    }
                )
        return dues_list

    def _get_document_values_consultar_odoofact(self, ose_supplier):
        return {
            "operacion": "consultar_comprobante",
            "tipo_de_comprobante": self.l10n_latam_document_type_id.type_of,
            "serie": str(self.sequence_prefix)[0:4],
            "numero": self.sequence_number,
        }

    def _get_document_values_anular_odoofact(self, ose_supplier):
        return {
            "operacion": "generar_anulacion",
            "tipo_de_comprobante": self.l10n_latam_document_type_id.type_of,
            "serie": str(self.sequence_prefix)[0:4],
            "numero": self.sequence_number,
            "motivo": self.l10n_pe_edi_cancel_reason or _("Null document"),
            "codigo_unico": "%s|%s|%s-%s"
            % (
                "odoo",
                self.company_id.partner_id.vat,
                str(self.sequence_prefix)[0:4],
                str(self.sequence_number),
            ),
        }

    def _get_detraction_type_of_lines(self):
        detraction_ids = self.invoice_line_ids.mapped(
            "product_id.l10n_pe_edi_detraction_type_id"
        )
        if (
            detraction_ids
            and self.partner_id.commercial_partner_id.country_code == "PE"
            and self.amount_total_signed
            >= self.company_id.l10n_pe_edi_min_amount_detraction
        ):
            return detraction_ids.sorted("rate", reverse=True)[0]
        return False

    def _get_description_without_product_code(self, product, description):
        if product and product.default_code:
            return (
                str(description).replace("[" + product.default_code + "]", "").strip()
            )
        return description

    def action_open_edi_request(self):
        """
        This method opens the EDI request
        """
        self.ensure_one()
        if self.l10n_pe_edi_request_id:
            return {
                "name": _("EDI Request"),
                "view_mode": "form",
                "res_model": "l10n_pe_edi.request",
                "res_id": self.l10n_pe_edi_request_id.id,
                "type": "ir.actions.act_window",
            }
        return True

    def _get_name_invoice_report(self):
        self.ensure_one()
        if (
            self.l10n_pe_edi_is_einvoice
            and self.company_id.account_fiscal_country_id.code == "PE"
        ):
            return "l10n_pe_edi_odoofact.report_invoice_document"
        return super()._get_name_invoice_report()

    def _get_amount_in_words(self):
        """Transform the amount to text"""
        if num2words is None:
            logging.getLogger(__name__).warning(
                "The library 'num2words' is missing, cannot render textual amounts."
            )
            return ""
        amount_base, amount = divmod(self.amount_total, 1)
        amount = round(amount, 2)
        amount = int(round(amount * 100, 2))

        lang_code = self.env.context.get("lang") or self.env.user.lang
        lang = self.env["res.lang"].search([("code", "=", lang_code)])
        words = num2words(amount_base, lang=lang.iso_code)
        result = _("%(words)s WITH %(amount)02d/100 %(currency_label)s") % {
            "words": words,
            "amount": amount,
            "currency_label": self.currency_id.currency_unit_label,
        }
        return result.upper()

    def _get_qr_code(self):
        commercial = self.commercial_partner_id
        commercial_doc_type = commercial.l10n_latam_identification_type_id
        return "|".join(
            [
                self.company_id and self.company_id.vat or "",
                self.l10n_latam_document_type_id
                and self.l10n_latam_document_type_id.code
                or "",
                self.sequence_prefix and str(self.sequence_prefix)[0:4] or "",
                str(self.sequence_number),
                str(self.l10n_pe_edi_amount_igv),
                str(self.amount_total),
                self.invoice_date and self.invoice_date.strftime("%d-%m-%Y") or "",
                commercial
                and commercial_doc_type
                and commercial_doc_type.l10n_pe_vat_code
                or "",
                commercial and commercial.vat or "",
            ]
        )
    
    @api.model
    def _send_daily_summary(self, date_sent):
        """
        Genera el resumen diario por fecha y compañia
        """
        companies = self.env['res.company'].search([], order='id asc')
        #moves = self.env['account.move'].search([('state', '=', 'posted'),('invoice_date', '=', date_sent),('l10n_pe_edi_legend_value','=',False)])
        #logging.info('{} moves'.format(len(moves)))
        logging.info(companies)
        idx = 1
        for company in companies:
            logging.info('{} company'.format(company.id))
            invoices = self.search([('state', '=', 'posted'),('invoice_date', '=', date_sent),('journal_id.l10n_pe_edi_is_einvoice','=',True), 
                ('move_type','=','out_invoice'), ('l10n_latam_document_type_id.code', '=', '03'), 
                ('l10n_pe_edi_legend_value','=',False), # ('l10n_pe_edi_sunat_accepted','=',False),
                ('company_id','=',company.id)])
            logging.info('{} invoices'.format(len(invoices)))
            # Connection to SSH Client
            # ssh = paramiko.SSHClient()
            # ssh.load_host_keys(os.path.expanduser(os.path.join("/root", ".ssh", "known_hosts")))
            # hostname = '51.79.53.219'
            # username = 'root'
            # password = 'CHd2JIYu'
            # ssh.connect(hostname, username=username, password=password)
            # sftp = ssh.open_sftp()
            # create json
            values = {}
            values["resumenDiario"] = []
            i = 1		
            for inv in invoices:
                # if inv.elec_serie_id.is_factelec:
                num_inv = str(inv.sequence_number).rjust(8, '0')
                line = {
                    "fecEmision": date_sent,
                    "fecResumen": date_sent,
                    "tipDocResumen": "03",
                    "idDocResumen": inv.name if "-" in inv.name and len(inv.name) == 13 else str(inv.sequence_prefix)[0:4] + "-" + num_inv,
                    "tipDocUsuario": inv.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
                    "numDocUsuario": inv.partner_id.vat,
                    "tipMoneda": inv.currency_id.name,
                    "totValGrabado": "%.2f" % inv.l10n_pe_edi_amount_base,
                    "totValExoneado": "%.2f" % inv.l10n_pe_edi_amount_exonerated,
                    "totValInafecto": "%.2f" % inv.l10n_pe_edi_amount_unaffected,
                    "totValExportado": "0",
                    "monValGratuito": "%.2f" % inv.l10n_pe_edi_amount_free,
                    "totOtroCargo": "0",
                    "totImpCpe": "%.2f" % inv.amount_total_signed,
                    "tipDocModifico": "",
                    "serDocModifico": "",
                    "numDocModifico": "",
                    "tipRegPercepcion": "",
                    "porPercepcion": "",
                    "monBasePercepcion": "",
                    "monPercepcion": "",
                    "monTotIncPercepcion": "",
                    "tipEstado": "1",
                    "tributosDocResumen": [
                        {
                            "idLineaRd": "%i"%i,
                            "ideTributoRd": "1000",
                            "nomTributoRd": "IGV",
                            "codTipTributoRd": "VAT",
                            "mtoBaseImponibleRd": "%.2f" % inv.l10n_pe_edi_amount_base,
                            "mtoTributoRd": "%.2f" % inv.l10n_pe_edi_amount_igv
                        }
                    ]
                }
                if inv.amount_tax == 0.00:
                    line["tributosDocResumen"].append(
                        {
                            "idLineaRd": "%i"%i,
                            "ideTributoRd": "9997",
                            "nomTributoRd": "EXO",
                            "codTipTributoRd": "VAT",
                            "mtoBaseImponibleRd": "%.2f" % inv.l10n_pe_edi_amount_base,
                            "mtoTributoRd": "0.00"
                        }
                    )
                values["resumenDiario"].append(line)
                i+=1
            if invoices:
                title = company.vat +'-RC-'+ date_sent[0:4] + date_sent[5:7] + date_sent[8:10] + '-' + str(idx) + '.JSON'
                path_file_rc = os.path.join(company.sfs_path, title)
                logging.info("path file -----------> {}, {}".format(title, path_file_rc))
                with open(path_file_rc, 'w') as f:
                    json.dump(values, f)
                # remotepath = os.path.join('/root/florencia/sfs/DATA', title)
                # sftp.put(path_file_rc, remotepath)
                # Close SSH Client
                # sftp.close()
                # ssh.close()
                idx += 1
    
    @api.model
    def _send_daily_summary_nc(self, date_sent):
        """
        Genera el resumen diario por fecha y compañia
        """
        companies = self.env['res.company'].search([])
        idx = 9
        for company in companies:
            invoices = self.search([('state', '=', 'posted'),('invoice_date', '=', date_sent),('journal_id.l10n_pe_edi_is_einvoice','=',True), 
                ('move_type','=','out_refund'), ('l10n_latam_document_type_id.code', '=', '07'), ('l10n_latam_document_type_id.doc_code_prefix','=','B'),
                ('edi_state','=','to_send'),('company_id','=',company.id)])
            values = {}
            values["resumenDiario"] = []
            i = 1		
            for inv in invoices:
                num_inv = str(inv.sequence_number).rjust(8, '0')
                line = {
                    "fecEmision": date_sent,
                    "fecResumen": date_sent,
                    "tipDocResumen": "07",
                    "idDocResumen": inv.name if "-" in inv.name and len(inv.name) == 13 else str(inv.sequence_prefix)[0:4] + "-" + num_inv,
                    "tipDocUsuario": inv.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
                    "numDocUsuario": inv.partner_id.vat,
                    "tipMoneda": inv.currency_id.name,
                    "totValGrabado": "%.2f" % inv.l10n_pe_edi_amount_base,
                    "totValExoneado": "%.2f" % inv.l10n_pe_edi_amount_exonerated,
                    "totValInafecto": "%.2f" % inv.l10n_pe_edi_amount_unaffected,
                    "totValExportado": "0",
                    "monValGratuito": "%.2f" % inv.l10n_pe_edi_amount_free,
                    "totOtroCargo": "0",
                    "totImpCpe": "%.2f" % inv.amount_total,

                    "tipDocModifico": "03",
                    "serDocModifico": str(inv.l10n_pe_edi_origin_move_id.sequence_prefix)[0:4],
                    "numDocModifico": str(inv.sequence_number).rjust(8, '0'),
                    "tipRegPercepcion": "",
                    "porPercepcion": "",
                    "monBasePercepcion": "",
                    "monPercepcion": "",
                    "monTotIncPercepcion": "",
                    "tipEstado": "1",
                    "tributosDocResumen": [
                        {
                            "idLineaRd": "%i"%i,
                            "ideTributoRd": "1000",
                            "nomTributoRd": "IGV",
                            "codTipTributoRd": "VAT",
                            "mtoBaseImponibleRd": "%.2f" % inv.l10n_pe_edi_amount_base,
                            "mtoTributoRd": "%.2f" % inv.l10n_pe_edi_amount_igv
                        }
                    ]
                }
                if inv.amount_tax == 0.00:
                    line["tributosDocResumen"].append(
                        {
                            "idLineaRd": "%i"%i,
                            "ideTributoRd": "9997",
                            "nomTributoRd": "EXO",
                            "codTipTributoRd": "VAT",
                            "mtoBaseImponibleRd": "%.2f" % inv.l10n_pe_edi_amount_base,
                            "mtoTributoRd": "0.00"
                        }
                    )
                values["resumenDiario"].append(line)
                i+=1
            if invoices:
                title = company.vat +'-RC-'+ date_sent[0:4] + date_sent[5:7] + date_sent[8:10] + '-' + str(idx) + '.JSON'
                path_file_rc = os.path.join(company.sfs_path, title)
                # print("path file -----------> ", title, path_file_rc)
                with open(path_file_rc, 'w') as f:
                    json.dump(values, f)
                idx += 1
