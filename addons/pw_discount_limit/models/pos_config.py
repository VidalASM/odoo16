# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    restrict_discount = fields.Boolean(string="Restrict Discount")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    restrict_discount = fields.Boolean(related='pos_config_id.restrict_discount', readonly=False)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_category(self):
        result = super(PosSession, self)._loader_params_product_category()
        result['search_params']['fields'].append('discount_limit')
        return result

    def _loader_params_product_product(self):
        result = super(PosSession, self)._loader_params_product_product()
        result['search_params']['fields'].append('product_discount_limit')
        return result
