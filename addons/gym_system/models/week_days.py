# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkoutSet(models.Model):
    _name = 'gym.weekdays'
    _rec_name = 'day'

    code = fields.Integer(string='Código', )
    day = fields.Char(string='Día')
