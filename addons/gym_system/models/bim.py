# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Bim(models.TransientModel):
    _name = 'gym.bim'
    _rec_name = 'height'
    _description = "Gym ingredient"

    height = fields.Float(default=1.75, string='Talla', required=True, )
    weight = fields.Float(default=70, string='Peso', required=True, )
    bmi = fields.Float(string='IMC', default=0.0, compute='_compute_bmi', )


    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for rec in self:
            rec.bmi = rec.weight / (rec.height * rec.height)
