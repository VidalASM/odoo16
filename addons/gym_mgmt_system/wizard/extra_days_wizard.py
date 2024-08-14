# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo.tools.translate import _
from odoo.tools import email_split
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models
from datetime import datetime, date, timedelta

import logging
_logger = logging.getLogger(__name__)


class ExtraDaysWizard(models.TransientModel):
    """
        A wizard to manage the creation/removal of aditional days on membership.
    """
    _name = 'extra.days.wizard'
    _description = 'Extra Days Membership'

    def _default_membership(self):
        return self.env['gym.membership'].browse(self._context.get('active_id'))

    def _default_member(self):
        return self.env['gym.membership'].browse(self._context.get('active_id')).member.id

    contract_id = fields.Many2one(comodel_name='gym.membership', string='Membresía', default=_default_membership, readonly=True)
    user_id = fields.Many2one(string='Usuario', comodel_name='res.users', default=lambda self: self.env.user)
    client_id = fields.Many2one('res.partner', string='Socio', compute="_get_member")
    reason_transfer = fields.Char(string='Motivo del registro')
    date_register = fields.Date(string='Fecha de registro', default=datetime.today())
    quantity_days = fields.Integer(string='Cantidad de días')

    @api.depends('contract_id')
    def _get_member(self):
        # ope_1 = (datetime.strptime(self.contract_id.membership_date_to, "%Y-%m-%d") - datetime.today())
        self.client_id = self.contract_id.member.id

    #Esta función crea el registro de dias adicionales
    def create_register(self):
        self.ensure_one()

        #Procedemos a crear la nueva membresia jalando datos del contrato seleccionado y de los datos que designamos con anterioridad.
        membership = self.env['membership.extra.days'].create({
            'name': self.contract_id.reference,
            'contract_id': self.contract_id.id,
            'user_id': self.user_id.id,
            'client_id': self.client_id.id,
            'reason_transfer': self.reason_transfer,
            'date_register': self.date_register,
            'quantity_days': self.quantity_days,
            'state_active': True,
        })

        #Ahora solo queda dar debaja este contrato.
        self.contract_id.membership_date_to = self.contract_id.membership_date_to + timedelta(days=self.quantity_days)

        #Si todo el proceso esta ok retornamos true
        return True
