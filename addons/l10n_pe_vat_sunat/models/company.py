# -*- coding: utf-8 -*-

from odoo import fields, models

class ResCompany(models.Model):
	_inherit = "res.company"

	annexed_locals = fields.Boolean('Annexed Locals')
	legal_representatives = fields.Boolean('Legal Representatives')