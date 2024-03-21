# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmLeadUpgrade(models.TransientModel):
    _name = "crm.lead.upgrade"
    _description = "Upgrade CRM Lead"

    def upgrade_crm_lead(self):
        Module = self.env['crm.lead']

        # install/upgrade: double-check preconditions
        Module._delete_opportunity()

        return {'type': 'ir.actions.act_window_close'}
    