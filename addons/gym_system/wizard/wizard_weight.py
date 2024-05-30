# -*- coding: utf-8 -*-

from odoo import models, fields


class Wizard_weight(models.TransientModel):
    _name = 'wizard.weight'
    _rec_name = 'weight'

    date = fields.Date(
        string='Date',
    )
    weight = fields.Float(
        string='Weight',
    )

    def weight_add(self):
        for rec in self:
            insweight = rec.weight
            active_id = self._context.get('active_id')
            workout_obj = self.env['gym.workout']
            workout_rec = workout_obj.browse(active_id)

            for rec in workout_rec:
                cid = rec.customer.id
            vals = {
                'customer_id': rec.customer.id,
                'date': self.date,
                'weight': insweight,
            }
        weight_obj = self.env['weight.entry'].create(vals).id
        aList = []
        aList.insert(1, weight_obj)
        return {
            'type': 'ir.actions.act_window',
            'name': 'gym_system.gym_weight_entry_form_view ',
            'res_model': 'weight.entry',
            'res_id': weight_obj,
            'domain': "[('id','in',[" + ','.join(map(str, aList)) + "])]",
            'view_mode': 'tree,form',
            'target': weight_obj,
        }
