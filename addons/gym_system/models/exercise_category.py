# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ExerciseCategory(models.Model):
    _name = 'exercise.category'
    _rec_name = 'exercise_category_id'

    category = fields.Selection([('acehold', 'Axe Hold'),
                                 ('barbell tricep extension', 'Barbell Tricep Extension')], string='Ejercicio',
                                )
    name = fields.Char(string='Seleccione su Ejercicio', )
    description = fields.Text(string='Descripción', )
    muscles_id = fields.Many2many('gym.muscle', string='Músculos Afectados', )
    equipment_id = fields.Many2one('product.product', string='Equipo', )
    image = fields.Image(string='Imagen', )
    exercise_id = fields.Many2one('exercise.select', string='Ejercicio En', )
    exercise_category_id = fields.Many2one('exercise.category.select', string='Ejercicio', )

