# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_pe_edi_provider = fields.Selection(selection_add=[('conflux', 'Conflux')])
    l10n_pe_edi_pse_client_id = fields.Char(string='PSE Client ID')
    l10n_pe_edi_pse_secret_key = fields.Char(string='PSE Secret Key')