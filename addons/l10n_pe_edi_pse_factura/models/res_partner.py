# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_pe_edi_retention_type = fields.Selection([
        ('01', 'Rate 3%'),
        ('02', 'Rate 6%'),
    ], string='IGV Retention Type')