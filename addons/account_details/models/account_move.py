# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    employee_id = fields.Many2one('hr.employee', string="Empleado")