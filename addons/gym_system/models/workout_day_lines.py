# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class GymDay(models.Model):
    _name = 'gym.day'
    _rec_name = 'day'

    day = fields.Datetime('Fecha')
    is_done = fields.Boolean('Realizado')
    workout_schedule_id = fields.Many2one('gym.workout', string="Horario de Entrenamiento")
    state = fields.Selection(selection=[
        ('new', 'Nuevo'),
        ('done', 'Realizado'),
        ('cancle', 'Cancelado'),
    ],
        string="Status", default=lambda self: _('new'), )


    def done(self):
        self.state = 'done'


    def cancle(self):
        self.state = 'cancle'


    def reset(self):
        self.state = 'new'
