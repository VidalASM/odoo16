# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    discount_limit = fields.Float(string="Discount Limit(%)")


class ProductTemplate(models.Model):
    _inherit = 'product.product'
    _inherit = 'product.template'

    product_discount_limit = fields.Float(string="Discount Limit(%)")
