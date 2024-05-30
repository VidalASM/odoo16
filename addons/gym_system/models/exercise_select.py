# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ExerciseSelect(models.Model):
    _name = 'exercise.select'
    _rec_name = 'name'

    name = fields.Char(string='Nombre', required=True)
