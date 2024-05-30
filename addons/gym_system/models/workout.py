# -*- coding: utf-8 -*-

import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api


class Workout(models.Model):
    _name = 'gym.workout'
    _recname = 'customer'
    customer = fields.Many2one('res.partner', string='Cliente', )
    from_date = fields.Date('Desde', )
    to_date = fields.Date('Hasta', )
    workout_id = fields.Many2one('gym.workouts', string='Rutina', )
    trainer_id = fields.Many2one('res.partner', string='Entrenador', )
    exercise_ids = fields.Many2many('exercise.category', string='Ejercicios', )
    day_ids = fields.One2many('gym.day', 'workout_schedule_id', string='Días', )


    @api.constrains('from_date', 'to_date')
    def _check_from_date(self):
        date_obj = self.env['gym.day']
        self.from_date_obj = datetime.datetime.strptime(self.from_date, '%Y-%m-%d')
        self.to_date_obj = datetime.datetime.strptime(self.to_date,'%Y-%m-%d')
        date = self.to_date_obj - self.from_date_obj
        date_range = self.from_date_obj + date
        data = 1
        days = []
        while (data <= date.days + 1):
            vals = {
                'day': self.from_date_obj
            }
            days_ids = date_obj.create(vals)
            days.append(days_ids.id)
            self.from_date_obj = self.from_date_obj + datetime.timedelta(1)
            data = data + 1
        self.day_ids = [(6, 0, days)]
