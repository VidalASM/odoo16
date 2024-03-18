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


class GymMember(models.Model):
    _name = "gym.member"
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Gym Member"


class MemberPartner(models.Model):
    _inherit = 'res.partner'

    gym_member = fields.Boolean(string='Socio', default=True)
    membership_count = fields.Integer('membership_count',
                                      compute='_compute_membership_count')
    measurement_count = fields.Integer('measurement_count',
                                       compute='_compute_measurement_count')
    state_client = fields.Selection(string='Estado Contrato',
        selection=[ ('1', 'Alianzado'), ('2', 'Espontáneo'), ('3', 'Invitado Espontáneo'),
                    ('4', 'Reinscripción'), ('5', 'Renovación'),('8', 'Invitado Referido'),('9', 'No atendido'),
                    ('happybirthday',u'Cumpleañeros de este mes'),('all', 'Todos') ], default='all', required=True)

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

    @api.onchange('gym_member')
    def _onchange_gym_member(self):
        """ select sale person to assign workout plan """
        if self.gym_member:
            return {
                'warning': {
                    'title': 'Warning!',
                    'message': 'select sale person (sales & purchase) '
                               'to assign workout plan'}
            }
