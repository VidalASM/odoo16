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

from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"    
    
    def get_lot_serial(self):
        lots = self.move_line_ids.mapped('lot_id.name')
        description = ''
        if lots:
            trj = ', '.join(lots)
            description = 'Lotes/Número de Serie: ' + '\n' + trj
        return description
