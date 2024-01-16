# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            partners = record.partner_id | record.partner_id.commercial_partner_id
            partners._increase_rank("supplier_rank")
        return res

class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchase_order_lines = fields.One2many('purchase.order.line', 'product_id', 
                                           string='Purchase Order Line that refers to partner')
    
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchase_order_lines = fields.Many2many('purchase.order.line', 
                                            compute='_compute_purchase_order_line', 
                                            string='Purchase Order Line that refers to partner')
    
    @api.depends('product_variant_ids.purchase_order_lines')
    def _compute_purchase_order_line(self):
        for record in self:
            pol = self.env['purchase.order.line'].search([('id','in',record.product_variant_ids.purchase_order_lines.ids)])
            record.purchase_order_lines = pol
            # record.standard_lst_price = 0.0
            # record.taxed_standard_lst_price = 0.0
            # if pol:
            #     record.standard_lst_price = pol[0].price_unit
            #     record.taxed_standard_lst_price = (pol[0].price_total + pol[0].additional_landed_cost) / pol[0].product_qty
