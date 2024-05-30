# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_pe_edi_pse_client_id = fields.Char(
        string="PSE Client ID",
        related="company_id.l10n_pe_edi_pse_client_id",
        readonly=False)
    l10n_pe_edi_pse_secret_key = fields.Char(
        string="PSE Secret Key",
        related="company_id.l10n_pe_edi_pse_secret_key",
        readonly=False)