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

from odoo import fields, models


class GymEquipments(models.Model):
    _inherit = 'product.template'

    gym_product = fields.Boolean(string='Producto de Gimnasio')
    company_ids = fields.Many2many(comodel_name='res.company', string='Acceso a')
    freeze_requests = fields.Integer(string='N° de solicitudes freeze')
    freeze_days = fields.Integer(string='Días freeze')
    session_fisio = fields.Integer(string='Citas Fisioterapia')
    session_nutri = fields.Integer(string='Citas Nutrición')
    day_start = fields.Date('Inicio')
    day_finish = fields.Date('Vence')
