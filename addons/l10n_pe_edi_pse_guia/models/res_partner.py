# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    l10n_pe_edi_address_type_code = fields.Char(string="Address Type Code", help="Code of the establishment that SUNAT has registered.")