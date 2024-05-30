# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import ValidationError


class ProductReportWiz(models.AbstractModel):
    _name = 'report.gym_system.workout_report'

    @api.model
    def render_html(self, docids, data=None):
        docs = self.env['gym.workout'].browse(data['ids'])
        if not docs:
            raise ValidationError("Data not found for print")
        docargs = {
            'doc_ids': data['ids'],
            'doc_model': 'gym.workout',
            'data': data,
            'docs': docs,
        }
        return self.env['report'].render('gym_system.workout_report', docargs)
