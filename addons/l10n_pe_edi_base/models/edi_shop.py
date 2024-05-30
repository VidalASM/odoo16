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


class EdiShop(models.Model):
    _name = "l10n_pe_edi.shop"
    _description = "EDI PE Shop"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "complete_name"
    _rec_names_search = ["name", "code"]
    _check_company_auto = True

    name = fields.Char(required=True)
    code = fields.Char(
        string="SUNAT Code",
        size=4,
        required=True,
        default="0000",
        help="Code from SUNAT",
    )
    complete_name = fields.Char(compute="_compute_complete_name", store=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=1,
        required=True,
    )
    l10n_pe_edi_ose_url = fields.Char(string="URL", tracking=True)
    l10n_pe_edi_ose_token = fields.Char(string="Token", tracking=True)
    l10n_pe_edi_ose_id = fields.Many2one(related="company_id.l10n_pe_edi_ose_id")
    l10n_pe_edi_ose_code = fields.Char(
        string="Code of PSE / OSE supplier",
        related="company_id.l10n_pe_edi_ose_id.code",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Address", tracking=True
    )
    send_email = fields.Boolean(
        string="Send invoice by Email",
        help="Send email automatically when the invoice is sent",
        tracking=True,
    )

    @api.depends("name", "code")
    def _compute_complete_name(self):
        for rec in self:
            if rec.name and rec.code:
                rec.complete_name = "%s %s" % (rec.name, rec.code)
            else:
                rec.complete_name = rec.name
