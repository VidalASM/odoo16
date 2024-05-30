# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class WorkoutScheduleReport(models.TransientModel):
    _name = 'workout.schedule.report'
    
    from_date = fields.Date(
        'From Date'
    )
    to_date = fields.Date(
        'To Date'
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    

    def print_workout_schedule(self):
        workout_obj = self.env['gym.workout'].search([('from_date', '=', self.from_date),('to_date', '<=', self.to_date)])
        if not workout_obj:
            raise ValidationError("No any workout set for %s on your selected date"%(self.customer_id.name))
        data = self.read()[0]
        data['ids'] = workout_obj.ids
        return self.env['report'].get_action(self, 'gym_system.workout_report', data = data)
        
