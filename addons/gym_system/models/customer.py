# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Customer(models.Model):
    _inherit = 'res.partner'


    trainer = fields.Boolean(string='Es Entrenador', )
    trainer_type = fields.Selection(selection=[('personal', 'Personal'), ('general', 'General'),
                                               ], default='general', )
