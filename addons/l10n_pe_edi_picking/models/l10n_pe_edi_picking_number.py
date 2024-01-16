# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

from odoo import models, fields, api, _

class EdiPickingNumber(models.Model):
    _inherit = 'l10n_pe_edi.picking.number'

    picking_id = fields.Many2one('stock.picking', string="E-Picking")

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        self.name = False
        if self.picking_id:
            self.name = self.picking_id.l10n_pe_edi_picking_name
            self.type = '1'
    
    @api.onchange('type')
    def _onchange_type(self):
        if self.type == '2':
            self.picking_id = False