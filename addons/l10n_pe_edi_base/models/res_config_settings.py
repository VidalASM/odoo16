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


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_pe_edi_send_invoice = fields.Boolean(
        related="company_id.l10n_pe_edi_send_invoice", readonly=False
    )
    l10n_pe_edi_ose_id = fields.Many2one(
        related="company_id.l10n_pe_edi_ose_id", readonly=False
    )
    l10n_pe_edi_send_invoice_interval_unit = fields.Selection(
        related="company_id.l10n_pe_edi_send_invoice_interval_unit",
        readonly=False,
    )
    l10n_pe_edi_send_invoice_next_execution_date = fields.Datetime(
        related="company_id.l10n_pe_edi_send_invoice_next_execution_date",
        readonly=False,
    )
    module_l10n_pe_edi_odoofact = fields.Boolean(string="Electronic Inviocing")
    module_l10n_pe_edi_picking = fields.Boolean(string="Electronic Remission Guide")
    module_odoope_ruc_validation = fields.Boolean(string="Data Validator - (PE)")
    module_l10n_pe_currency = fields.Boolean(string="Exchange Rate of the Day - (PE)")
