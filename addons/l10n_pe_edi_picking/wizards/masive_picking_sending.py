# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2019-TODAY Odoo Peru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class MasivePickingSending(models.TransientModel):
    _name = 'masive.picking.sending'
    _description = "Masive Picking Sending"

    def send_masive(self):
        active_ids = self.env.context.get('active_ids',[])
        picking_ids = self.env['stock.picking'].browse(active_ids)
        for pick in picking_ids:
            pick.action_document_send()
        return True