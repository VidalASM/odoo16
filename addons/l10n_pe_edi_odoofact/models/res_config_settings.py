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

    module_l10n_pe_edi_odoofact_pro = fields.Boolean(string="Electronic Inviocing Pro")
    module_l10n_pe_edi_odoofact_sale = fields.Boolean(
        string="Electronic Inviocing Sale"
    )
    l10n_pe_edi_min_amount_retention = fields.Float(
        related="company_id.l10n_pe_edi_min_amount_retention", readonly=False
    )
    l10n_pe_edi_min_amount_detraction = fields.Float(
        related="company_id.l10n_pe_edi_min_amount_detraction", readonly=False
    )
    l10n_pe_edi_detraction_payment_type_id = fields.Many2one(
        related="company_id.l10n_pe_edi_detraction_payment_type_id", readonly=False
    )
    l10n_pe_edi_detraction_bank_account_id = fields.Many2one(
        related="company_id.l10n_pe_edi_detraction_bank_account_id", readonly=False
    )
    l10n_pe_edi_company_partner_id = fields.Many2one(related="company_id.partner_id")
