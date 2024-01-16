# -*- coding: utf-8 -*-

from odoo import models, fields


class WorkoutSet(models.Model):
    _name = 'gym.workouts'

    name = fields.Char('Name')
    exercise_ids = fields.Many2many('exercise.category', string='Ejercicio', )
    week_days_ids = fields.Many2many('gym.weekdays', string='Días')
