# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PosConfig(models.Model):
	_inherit = "pos.config"

	restrict_zero_qty = fields.Boolean(string='Restrict Zero Quantity')


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	restrict_zero_qty = fields.Boolean(related="pos_config_id.restrict_zero_qty",readonly=False)


class PosSession(models.Model):
	_inherit = 'pos.session'

	def _loader_params_product_product(self):
		result = super()._loader_params_product_product()
		result['search_params']['fields'].extend(['qty_available','type'])
		return result

