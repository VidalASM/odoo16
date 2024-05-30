# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Ingredients(models.Model):
    _name = 'gym.ingredient'
    _description = "Gym ingredient"
    name = fields.Char(string='Nombre', required=True, )
    unit_id = fields.Many2one('product.uom', string="Unidad de Medida", )
    value_in = fields.Char(string='Valor En', )
    energy = fields.Float(string='Energia', )
    protein = fields.Float(string='Proteina', )
    carbohydrates = fields.Float(string='Carbohidratos', )
    sugerincarbohydrates = fields.Float(string='Azúcar en Carbohidratos', )
    fat = fields.Float(string='Grasa', )
    staturated = fields.Float(string='Contenido de Grasas Saturadas en Grasas', )
    fibres = fields.Float(string='Fibras ', )
    sodium = fields.Float(string='Sodio', )
    ingredient_id = fields.Many2one('gym.nutrition', 'Nutrición')
