#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # ==== Business fields ====
    l10n_pe_edi_free_product = fields.Boolean(
        string="Free",
        compute="_compute_l10n_pe_edi_free_product",
        help="Is free product?",
    )
    l10n_pe_edi_tax_type = fields.Many2one(
        comodel_name="l10n_pe_edi.catalog.07",
        string="Tax Type",
        compute="_compute_l10n_pe_edi_tax_type",
        store=True,
        readonly=False,
    )
    l10n_pe_edi_advance_serie = fields.Char(string="Advance Serie")
    l10n_pe_edi_advance_number = fields.Integer(string="Advance Number")

    # === Amount fields ===
    l10n_pe_edi_price_unit_excluded = fields.Float(
        string="Price unit excluded",
        digits=(12, 10),
        compute="_compute_l10n_pe_edi_amounts",
        help="Price unit without taxes",
    )
    l10n_pe_edi_price_unit_included = fields.Float(
        string="Price unit IGV included",
        digits=(12, 10),
        compute="_compute_l10n_pe_edi_amounts",
        help="Price unit with IGV included",
    )
    l10n_pe_edi_amount_discount = fields.Monetary(
        string="Amount discount before taxes",
        compute="_compute_l10n_pe_edi_amounts",
        currency_field="currency_id",
    )
    l10n_pe_edi_igv_amount = fields.Monetary(
        string="IGV amount",
        compute="_compute_l10n_pe_edi_amounts",
        currency_field="currency_id",
    )
    l10n_pe_edi_amount_free = fields.Float(
        string="Free amount",
        digits=(12, 10),
        compute="_compute_l10n_pe_edi_amounts",
        help="amount calculated if the line id for free product",
    )
    l10n_pe_edi_icbper_amount = fields.Monetary(
        string="ICBPER amount",
        compute="_compute_l10n_pe_edi_amounts",
        currency_field="currency_id",
    )

    @api.depends(
        "quantity",
        "discount",
        "price_unit",
        "tax_ids",
        "currency_id",
        "l10n_pe_edi_free_product",
    )
    def _compute_l10n_pe_edi_amounts(self):
        for line in self:
            line.l10n_pe_edi_price_unit_excluded = line.price_unit
            line.l10n_pe_edi_price_unit_included = line.price_unit
            line.l10n_pe_edi_igv_amount = 0.0
            line.l10n_pe_edi_amount_discount = 0.0
            line.l10n_pe_edi_amount_free = 0.0

            if line.display_type == "product" and line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line.price_unit,
                    quantity=1.0,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.l10n_pe_edi_price_unit_excluded = taxes_res["total_excluded"]
                line.l10n_pe_edi_price_unit_included = taxes_res["total_included"]
                line_discount_price_unit = line.price_unit * (
                    1 - (line.discount / 100.0)
                )
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                igv_taxes_ids = line.tax_ids.filtered(
                    lambda r: r.tax_group_id.name == "IGV"
                )
                line.l10n_pe_edi_igv_amount = sum(
                    x["amount"]
                    for x in taxes_res["taxes"]
                    if x["id"] in igv_taxes_ids.ids
                )
                icbper_taxes_ids = line.tax_ids.filtered(
                    lambda r: r.tax_group_id.name == "ICBPER"
                )
                line.l10n_pe_edi_icbper_amount = sum(
                    x["amount"]
                    for x in taxes_res["taxes"]
                    if x["id"] in icbper_taxes_ids.ids
                )
            if not line.l10n_pe_edi_free_product:
                line.l10n_pe_edi_amount_discount = (
                    line.l10n_pe_edi_price_unit_excluded
                    * (line.discount / 100)
                    * line.quantity
                )
            else:
                line.l10n_pe_edi_amount_free = line.price_unit * line.quantity

    @api.depends("discount")
    def _compute_l10n_pe_edi_free_product(self):
        for line in self:
            line.l10n_pe_edi_free_product = True if line.discount == 100.0 else False

    @api.depends("product_id", "product_uom_id", "l10n_pe_edi_free_product")
    def _compute_tax_ids(self):
        res = super(AccountMoveLine, self)._compute_tax_ids()
        for line in self:
            if (
                line.move_id.move_type == "out_invoice"
                and line.display_type == "product"
                and line.l10n_pe_edi_free_product
            ):
                line.tax_ids = [(6, 0, [self.env.ref("l10n_pe.1_sale_tax_gra").id])]
        return res

    @api.depends("tax_ids", "move_id.l10n_pe_edi_odoofact_operation_type")
    def _compute_l10n_pe_edi_tax_type(self):
        tax_type = self.env["l10n_pe_edi.catalog.07"]
        for line in self:
            if any(tax.l10n_pe_edi_tax_code in ["9996"] for tax in line.tax_ids):
                # the commented code can be used for the filter when showing the
                # dropdown list of igv types
                # free_tax_type = tax_type.filtered(lambda x:
                # free_tax.l10n_pe_edi_tax_code in str(x.tribute_code).split("-"))
                line.l10n_pe_edi_tax_type = tax_type.search(
                    [("code", "=", "15")], limit=1
                ).id
            elif any(tax.l10n_pe_edi_tax_code in ["9997"] for tax in line.tax_ids):
                line.l10n_pe_edi_tax_type = tax_type.search(
                    [("code", "=", "20")], limit=1
                ).id
            elif any(tax.l10n_pe_edi_tax_code in ["9998"] for tax in line.tax_ids):
                line.l10n_pe_edi_tax_type = tax_type.search(
                    [("code", "=", "30")], limit=1
                ).id
                if line.move_id.l10n_pe_edi_odoofact_operation_type in ["2", "3"]:
                    line.l10n_pe_edi_tax_type = tax_type.search(
                        [("code", "=", "40")], limit=1
                    ).id
            elif any(tax.l10n_pe_edi_tax_code in ["9995"] for tax in line.tax_ids):
                line.l10n_pe_edi_tax_type = tax_type.search(
                    [("code", "=", "40")], limit=1
                ).id
            else:
                line.l10n_pe_edi_tax_type = tax_type.search(
                    [("code", "=", "10")], limit=1
                ).id
