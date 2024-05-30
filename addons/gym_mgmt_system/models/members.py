# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Shahul Faiz (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import fields, models, api
from datetime import datetime, timedelta


class GymMember(models.Model):
    _name = "gym.member"
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Gym Member"


class TutorType(models.Model):
    _name = "tutor.type"
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Tipo de Parentesco"

    name = fields.Char(string='Nombre')
    description = fields.Text(string='Descripción')


class MemberPartner(models.Model):
    _inherit = 'res.partner'

    gym_member = fields.Boolean(string='Socio', default=True)
    membership_count = fields.Integer('membership_count',
                                      compute='_compute_membership_count')
    measurement_count = fields.Integer('measurement_count',
                                       compute='_compute_measurement_count')
    state_client = fields.Selection(string='Estado Contrato',
        selection=[ ('1', 'Alianzado'), ('2', 'Espontáneo'), ('3', 'Invitado Espontáneo'),('4', 'Reinscripción'), ('5', 'Renovación'),
                    ('6', 'Activo'),('7', 'Bloqueado'),('8', 'Invitado Referido'),('9', 'No atendido'),
                    ('happybirthday',u'Cumpleañeros de este mes'),('all', 'Todos'), ], default='all', required=True)
    # Apoderado
    has_tutor = fields.Boolean(string='Tiene Apoderado?', default=False)
    tutor_id = fields.Many2one('res.partner', string='Apoderado')
    tutor_relation = fields.Many2one('tutor.type', string='Parentesco')
    # Hijos
    child_ids = fields.One2many(comodel_name='res.partner', inverse_name='tutor_id', string='Hijos')
    # Referidos
    referred_ids = fields.One2many(comodel_name='referred.record', inverse_name='partner_id', string='Invitados Referidos')
    
    def _compute_membership_count(self):
        """ number of membership for gym members """
        for rec in self:
            rec.membership_count = rec.env['gym.membership'].search_count([
                ('member.id', '=', rec.id)])

    def _compute_measurement_count(self):
        """ number of measurements for gym members """
        for rec in self:
            rec.measurement_count = rec.env['measurement.history'].search_count(
                [('member.id', '=', rec.id)])

    # @api.onchange('gym_member')
    # def _onchange_gym_member(self):
    #     """ select sale person to assign workout plan """
    #     if self.gym_member:
    #         return {
    #             'warning': {
    #                 'title': 'Warning!',
    #                 'message': 'select sale person (sales & purchase) '
    #                            'to assign workout plan'}
    #         }

class ReferredRecord(models.Model):
    _name = 'referred.record'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string='Nombre', required=True, copy=False, readonly=True, index=True, default=lambda self:'Nuevo')
    description = fields.Text(string='Descripción')
    date = fields.Date(string='Fecha', default=(lambda self: fields.datetime.now() - timedelta(hours=5)), required=True)
    quantity_days = fields.Integer(string='Número de Días', default=30)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Socio', ondelete='cascade', required=True)
    contract_id = fields.Many2one(comodel_name='gym.membership', string='Membresía', ondelete='cascade', required=True)
    referred_id = fields.Many2one(comodel_name='res.partner', string='Invitado / Referido', ondelete='cascade', required=True)
    counter_id = fields.Many2one(comodel_name='res.users', string="Por", index=True, default=lambda self: self.env.user)
    company_id = fields.Many2one(comodel_name='res.company', string='Sede', store=True, readonly=True, default=lambda self: self.env.company)
    state = fields.Selection(string='Estado', selection=[('activa', 'Activo'), ('inactiva', 'Inactivo')], default="activa")

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            if 'partner_id' in vals and 'contract_id' in vals:
                contract = self.env['gym.membership'].browse(vals['contract_id'])
                vals['name'] = (contract.name if contract else '') #+ ' - ' + (partner.name if partner else '')
        result = super(ReferredRecord, self).create(vals)
        return result
     