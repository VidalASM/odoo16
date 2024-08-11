# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo.tools.translate import _
from odoo.tools import email_split
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models
from datetime import datetime, date, timedelta
import calendar
import copy

import logging
_logger = logging.getLogger(__name__)


class AttendanceWizard(models.TransientModel):
    """
        A wizard to manage the creation of attendance record.
    """
    _name = 'attendace.wizard'
    _description = 'Create Attendance Record'

    vat = fields.Char(string=u'Documento de identificación')
    partner_id = fields.Many2one(string=u'Socio', comodel_name='res.partner')
    contract_id = fields.Many2one(string=u'Contrato', comodel_name='gym.membership')
    image = fields.Binary("Foto")
    info = fields.Text(string=u'Detalles', readonly=True, store=True)
    state = fields.Selection(string='Estado', selection=[('active', 'Activo'), ('inactive', 'Inactivo'), ('freezing', 'Freezing'),('pending', 'Pendiente'),],default='pending')
    plan = fields.Text(string='Plan')
    days_end = fields.Integer(string=u'Días restantes')
    count_referred = fields.Integer(string=u'Referidos mensuales', default=0)
    update_message = fields.Char(string='Mensaje')

    @api.onchange('vat')
    def _onchange_vat(self):
        self.partner_id = False
        self.image = False
        self.contract_id = False

        if not self.vat:
            return False

        partner_id = self.env['res.partner'].search([('vat', '=', self.vat)])
        if partner_id and len(partner_id) == 1:
            self.partner_id = partner_id
            self.info = ""
        if not partner_id:
            self.info = "No se encontraron coincidencias con ese documento"
        if len(partner_id) >= 2:
            self.info = "Se encontraron muchas coincidencias con ese documento"

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if not self.partner_id:
            return False

        self.image = self.partner_id.image_1920
        memberships = self.env['gym.membership'].search([
            ('member', '=', self.partner_id.id),
            ('state','in',['draft','confirm']),
            ('membership_date_from','<=', fields.Date.today()),
            ('membership_date_to','>=', fields.Date.today()),
            # ('invoice_id.amount_residual','=',0.0),
            ], order="membership_date_from asc")

        if memberships:
            result = {'domain' :{'contract_id' : [('id','in',memberships.ids)]}}
            self.contract_id = memberships[0]
            return result
        self.info = "No se encontraron ventas aprobadas"
        return False

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        if not self.contract_id:
            return False
        
        self.days_end = abs((self.contract_id.membership_date_to - date.today()).days)
        company_id = self.env.company
        self.info = "Le quedan "+str(self.days_end)+" días de contrato\nSede del contrato: "+str(self.contract_id.company_id.name)\
                    +"\nFecha de finalización: "+str(self.contract_id.membership_date_to)+"\nSede de acceso: "+str(company_id)
        self.state = self.contract_id.state_contract
        self.plan = self.contract_id.membership_scheme.name
        # Numero de referidos
        referred = self.env['referred.record']
        c_month = datetime.today().month
        c_year = datetime.today().year
        start_date = datetime(c_year, c_month, 1)
        end_date = datetime(c_year, c_month, calendar.mdays[c_month])
        count_referred = referred.search([('date','>=',start_date), ('date','<=',end_date),
            ('partner_id','=',self.contract_id.member.id), ('state','=','activa')])
        if count_referred:
            self.count_referred = len(count_referred)

    def notification(self, title, type):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': 'Your Custom Message',
                'type': type,  #types: success,warning,danger,info
                'sticky': False,  #True/False will display for few seconds if false
            },
        }
        # _logger.info('---> notification')
        return notification


    def attendance_record(self):
        if self.contract_id:
            self.contract_id.attendance_record()
            # pname = copy.copy(self.partner_id.name)
            pname = self.contract_id.member.name
            self.update_message = "Asistencia Marcada: %s, %s, %s" %(self.vat, pname, str(fields.datetime.now()))
            self.vat = ''

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Asistencia',
                'type': 'success',
                'message': '¡Marcación de asistencia exitosa!',
                'sticky': True,
            }
        }
        self.notification('Asistencia', 'success')

        action = self.env["ir.actions.actions"]._for_xml_id("gym_mgmt_system.action_create_attendance_wizard")
        action['res_id'] = self.id
        return action

    def attendance_record_out(self):
        if self.contract_id:
            self.contract_id.attendance_out()
            self.update_message = "Salida: %s, %s, %s" %(self.vat, self.partner_id.name, str(fields.datetime.now()))
            self.vat = ''

        action = self.env["ir.actions.actions"]._for_xml_id("gym_mgmt_system.action_create_attendance_wizard")
        action['res_id'] = self.id
        return action

    @api.onchange('image')
    def _onchange_image(self):
        if self.contract_id:
            partner = self.contract_id.member
            partner.write({'image_1920': self.image,})    
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Imagen',
                    'type': 'success',
                    'message': '¡Cambio de Imagen exitoso!',
                    'sticky': True,
                }
            }
            return notification
