# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging
log = logging.getLogger(__name__)

class AccountInvoiceTransportReferences(models.Model):
    _name = 'account.move.l10n_pe_transportref'

    move_id = fields.Many2one(
        'account.move', string='Invoice', ondelete='cascade', index=True)
    ref_type = fields.Selection([('09', 'GR REMITENTE'), (
        '31', 'GR TRANSPORTISTA')], string="Type of despatch", default='09')
    ref_number = fields.Char('Number Reference', required=True, default='')