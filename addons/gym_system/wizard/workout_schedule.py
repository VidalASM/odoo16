# -*- coding: utf-8 -*-

from odoo import models, fields


class Wizard_weight(models.TransientModel):
    _name = 'workout.schedule'

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer'
    )
    from_date = fields.Datetime(
        string='From Date',
    )
    to_date = fields.Datetime(
        string='To Date',
    )
    workout_id = fields.Many2one(
        'gym.workouts',
        'Workout'
    )
    trainer_id = fields.Many2one(
        'res.partner',
        'Trainer'
    )

    def create_workout_schedule(self):
        workout_sche_obj = self.env['gym.workout']
        vals = {
            'customer': self.customer_id.id,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'workout_id': self.workout_id.id,
            'trainer_id': self.trainer_id.id,
            'exercise_ids': [(6, 0, self.workout_id.exercise_ids.ids)],
        }
        workout_obj = workout_sche_obj.create(vals).id
        aList = []
        aList.insert(1, workout_obj)
        return {
            'type': 'ir.actions.act_window',
            'name': 'gym_system.workout_overview_form_view',
            'res_model': 'gym.workout',
            'res_id': workout_obj,
            'domain': "[('id','in',[" + ','.join(map(str, aList)) + "])]",

            'view_mode': 'tree,form',
            'target': workout_obj,
        }
