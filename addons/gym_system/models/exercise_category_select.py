# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ExerciseCategorySelect(models.Model):
    _name = 'exercise.category.select'
    _rec_name = 'name'

    name = fields.Char( string='Ejercicio',required=True,    )
    body_parts_id = fields.Many2one( 'exercise.select', string='Parte del Cuerpo',)
