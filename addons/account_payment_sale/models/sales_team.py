# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    available_payment_mode_ids = fields.Many2many('account.payment.mode', 
        relation='l10n_pe_sales_team_available_account_payment_rel', column1='sale_team_id', column2='payment_mode_id',
        string='Modos de pago disponibles')
    