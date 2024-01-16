# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Nutrition(models.Model):
    _name = 'gym.nutrition'
    _rec_name = 'customer_id'

    customer_id = fields.Many2one('res.partner', string='Cliente', required=True, )
    nutrition_ids = fields.Many2many('gym.ingredient', string='Ingredientes')
    date = fields.Date(string='Fecha', required=True, default=fields.Datetime.now, )
