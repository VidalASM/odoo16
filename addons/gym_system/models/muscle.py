# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Muscle(models.Model):
    _name = 'gym.muscle'
    name = fields.Char(string='Nombre')
    description = fields.Text(string='Descripción', )
    image = fields.Image(string='Imagen', )
    typeside = fields.Selection([('front_side', 'Lado Frontal'), ('back_side', 'Lado Trasero')], string='Tipo', )
    exercise_category_id = fields.Many2many('exercise.category.select', string='Categoría de Ejercicio')

