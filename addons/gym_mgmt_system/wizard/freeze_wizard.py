# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo.tools.translate import _
from odoo.tools import email_split
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)


class FreezeWizard(models.TransientModel):
    """
        A wizard to manage the creation/removal of freeze membership.
    """
    _name = 'freeze.wizard'
    _description = 'Grant Freeze membership'

    def _default_membership(self):
        return self.env['gym.membership'].browse(self._context.get('active_id'))

    contract_id = fields.Many2one(comodel_name='gym.membership', string='Membresía', default=_default_membership, readonly=True)
    number_freeze = fields.Char(string='Nro de Solicitud')
    cause = fields.Char(string='Motivo del freeze')
    date_freeze = fields.Date(string='Fecha registrada', default=fields.Date.today, readonly=True)
    start_date = fields.Date(string='Desde', default=fields.Date.today, required=True)
    end_date = fields.Date(string='Reinicio', required=True)
    quantity_days = fields.Integer(string='Días de freeze', required=True)
    counter_id = fields.Many2one(comodel_name='res.users', string="Responsable", default=lambda self: self.env.user, readonly=True)
    is_force = fields.Selection(string='Forzado', selection=[('si', 'Si'), ('no', 'No')], default='no')

    @api.onchange('start_date', 'quantity_days')
    def _onchange_start_date(self):
        if self.start_date:
            start = fields.Datetime.from_string(self.start_date)
            self.end_date = start + timedelta(days=self.quantity_days + 1, seconds=-1)
        else:
            raise ValidationError("Defina una fecha de inicio porfavor")

    def create_freeze(self):
        # Validación del freeze
        self.ensure_one()
        if self.is_force == 'no':
            scheme_days_freeze = self.contract_id.membership_scheme.freeze_days
            contract_days_freeze = sum(self.contract_id.freeze_ids.mapped('quantity_days')) if self.contract_id.freeze_ids else 0
            partition_days_freeze = scheme_days_freeze - contract_days_freeze
            if self.quantity_days > scheme_days_freeze:
                self.end_date = ""
                raise ValidationError("El limite de días disponibles es %s" %(scheme_days_freeze))
            elif partition_days_freeze <= 0:
                raise ValidationError("Ya no le quedan solicitudes disponibles")
        # Creacion de freeze
        self.env['membership.freeze'].create({
            'number_freeze': self.number_freeze,
            'contract_id': self.contract_id.id,
            'counter_id': self.counter_id.id,
            'cause': self.cause,
            'date_freeze': datetime.today(),
            'start_date': self.start_date,
            'quantity_days': self.quantity_days,
            'end_date': self.end_date,
            'is_force': self.is_force,
            'state_freeze':True,
        })
        #Terminamos la función con la actualización del start_date con el start_date_new del del wizard
        # end = fields.Datetime.from_string(self.contract_id.date_end)
        self.contract_id.membership_date_to = self.contract_id.membership_date_to + timedelta(days=self.quantity_days)
        #*Si tiene un contrato a futuro modificamos su fecha de inicio y su fecha de finalizacion
        future_contracts = self.getFutureContract(self.contract_id.member, self.contract_id.membership_date_from)
        if future_contracts:
            memberships = self.env['gym.membership'].browse(future_contracts)
            for m in memberships:
                m.membership_date_from = m.membership_date_from + timedelta(days=self.quantity_days)
                m.membership_date_to = m.membership_date_to + timedelta(days=self.quantity_days)
        return True
    
    #Si tuviera otro contrato a futuro este tendra que cambiar su fecha de incio
    def getFutureContract(self, partner, date_end):
        future_contracts = self.env['gym.membership'].search([
            ('member', '=', partner.id),
            ('membership_date_from','>',date_end),
        ])
        # print("Dentro de la funcion ", future_contracts)
        contract_future = []
        if future_contracts:
            for contract in future_contracts:
                contract_future.append(contract.id)
            # print("Retornando el contrato",contract_future)
            return contract_future
        else:
            return False

    # def action_apply(self):
    #     self.ensure_one()
    #     self.user_ids.action_apply()
    #     return {'type': 'ir.actions.act_window_close'}

class FreezeRebootWizard(models.TransientModel):
    """
        A wizard to manage the creation/removal of freeze membership.
    """
    _name = 'freeze.reboot.wizard'
    _description = 'Reboot Freeze membership'

    def _default_membership(self):
        return self.env['gym.membership'].browse(self._context.get('active_id'))

    def _default_start(self):
        membership = self.env['gym.membership'].browse(self._context.get('active_id'))
        freeze = self.env['membership.freeze'].search([('contract_id','=',membership.id)], order="id desc", limit=1)
        if freeze:
            return freeze.start_date
        else:
            return False

    def _default_end(self):
        membership = self.env['gym.membership'].browse(self._context.get('active_id'))
        freeze = self.env['membership.freeze'].search([('contract_id','=',membership.id)], order="id desc", limit=1)
        if freeze:
            return freeze.end_date
        else:
            return False

    contract_id = fields.Many2one(comodel_name='gym.membership', string='Membresía', default=_default_membership, readonly=True)
    start_date = fields.Date(string='Desde', default=_default_start, readonly=True)
    end_date = fields.Date(string='Reinicio', default=_default_end, readonly=True)
    reboot_date = fields.Date(string='Nuevo Reinicio',  default=fields.Date.today, required=True)

    def reboot_freeze(self):
        # Levantamiento del freeze
        self.ensure_one()
        freeze = self.env['membership.freeze'].search([('contract_id','=',self.contract_id.id)], order="id desc", limit=1)
        scheme_days_freeze = self.reboot_date
        contract_days_freeze = freeze.start_date
        partition_days_freeze = abs((scheme_days_freeze - contract_days_freeze).days)
        freeze.write({'end_date': self.reboot_date, 'quantity_days': partition_days_freeze})
        
        res = self.contract_id.membership_date_from
        templ = self.contract_id.membership_scheme.product_tmpl_id
        date = fields.Date.from_string(self.contract_id.membership_date_from)
        if self.contract_id.type_contract == '3':
            res = date + timedelta(days=self.contract_id.days_transferred)
        elif templ.membership_type == "variable":
            delta = templ.membership_interval_qty
            if templ.membership_interval_unit == "days":
                res = date + timedelta(days=delta)
            elif templ.membership_interval_unit == "weeks":
                res = date + timedelta(weeks=delta)
            elif templ.membership_interval_unit == "months":
                res = date + relativedelta(months=delta)
            elif templ.membership_interval_unit == "years":
                res = date + relativedelta(years=delta)
        
        contract_days_freeze = sum(self.contract_id.freeze_ids.mapped('quantity_days')) if self.contract_id.freeze_ids else 0
        res += timedelta(days=contract_days_freeze)
        
        self.contract_id.write({'membership_date_to': res})
