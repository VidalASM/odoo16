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

class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_pe_edi_picking_partner_for_carrier_driver = fields.Boolean(string="Use partners for Carrier and Driver")
    l10n_pe_edi_picking_partner_for_starting_arrival_point = fields.Boolean(string="Use partners for Starting and Arrival Point")

    def get_doc_types(self):
        res = super(ResCompany, self).get_doc_types()
        res.append('00')
        return res
    
    def get_picking_dict(self, picking_ids):
        pickings = self.env['stock.picking'].browse(picking_ids)
        return [{
            'shop': picking.l10n_pe_edi_shop_id and picking.l10n_pe_edi_shop_id.name or '',
            'date': picking.date_done,
            'type_code': '00',
            'type': _('Picking'),
            'name': picking.l10n_pe_edi_picking_name,
            'ose': picking.l10n_pe_edi_ose_accepted,
            'sunat': picking.l10n_pe_edi_sunat_accepted,
            'error': picking.l10n_pe_edi_response,
        } for picking in pickings]
    
    def get_data_dict(self, edi_requests):
        res = super(ResCompany, self).get_data_dict(edi_requests)
        data = []
        if edi_requests:
            picking_edi_requests = [x for x in edi_requests if x['type'] == 'picking']
            picking_ids = [x['res_id'] for x in picking_edi_requests]
            data = self.get_picking_dict(picking_ids)
        return res + data
    
    def get_email_template_lines(self):
        res = super(ResCompany, self).get_email_template_lines()
        res += _("<li>(--00_count--) PICKING NOT SENT AND / OR NOT ACCEPTED</li>")
        return res
    
    def replace_body_html(self, body_html, days, date, type_count):
        res = super(ResCompany, self).replace_body_html(body_html, days, date, type_count)
        res = res.replace('--00_count--', str(type_count['00']))
        return res
