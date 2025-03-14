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


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_pe_edi_min_amount_retention = fields.Float(string="Min Amount for Retention")
    l10n_pe_edi_min_amount_detraction = fields.Float(string="Min Amount for Detraction")
    l10n_pe_edi_detraction_payment_type_id = fields.Many2one(
        comodel_name="l10n_pe_edi.catalog.59",
        string="Detraction Payment Type",
        copy=False,
    )
    l10n_pe_edi_detraction_bank_account_id = fields.Many2one(
        comodel_name="res.partner.bank", string="National bank Account"
    )
    sfs_path = fields.Char(string="SFS Location")
