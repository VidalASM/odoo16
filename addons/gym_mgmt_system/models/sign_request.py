# -*- coding: utf-8 -*-
from odoo import api, fields, models, http, _, Command

class SignRequest(models.Model):
    _inherit = "sign.request"

    membership = fields.Many2one('gym.membership', string='Membresía', tracking=True, required=False)
    membership_date_to = fields.Date(string='Fecha de vigencia', related="membership.membership_date_to", store=True)

class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    membership = fields.Many2one('gym.membership', string='Membresía', tracking=True, required=False)

    def create_request(self):
        sign_request = super(SignSendRequest, self).create_request()
        sign_request.write({
            'membership': self.membership.id,
        })
        return sign_request

