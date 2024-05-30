# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CalorieCal(models.Model):
    _name = 'gym.calorie'
    _rec_name = 'name_id'

    name_id = fields.Many2one('res.partner', string='Nombre',
                              )
    age = fields.Float(string='Edad', )
    height = fields.Float(string='Talla', )
    gender = fields.Selection([('male', 'Masculino'), ('female', 'Femenino')], string='Género',
                              )
    weight = fields.Float(string='Peso', )
    bmr = fields.Float(string='TMB', compute='_compute_bmr', )


    @api.depends('height', 'weight', 'age')
    def _compute_bmr(self):
        for rec in self:
            rec.bmr = 66.47 + \
                      (13.75 * rec.weight) + (5.0 * rec.height) - (6.75 * rec.age)
