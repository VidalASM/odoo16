from odoo.tests import common
from odoo.tests import Form


class TestInvoiceTypeDocumentExtension(common.TransactionCase):

    def test_computed_fields(self):

        warehouse = self.env['stock.warehouse'].search([], limit=1)
        warehouse.write({'reception_steps': 'three_steps'})
        warehouse.mto_pull_id.route_id.active = True
        self.env['stock.location']._parent_store_compute()
        warehouse.reception_route_id.rule_ids.filtered(
            lambda p: p.location_src_id == warehouse.wh_input_stock_loc_id and
                      p.location_dest_id == warehouse.wh_qc_stock_loc_id).write({
            'procure_method': 'make_to_stock'
        })

        finished_product = self.env['product.product'].create({
            'name': 'Finished Product',
            'type': 'product',
        })
        component = self.env['product.product'].create({
            'name': 'Component',
            'type': 'product',
            'route_ids': [(4, warehouse.mto_pull_id.route_id.id)]
        })
        self.env['stock.quant']._update_available_quantity(component, warehouse.wh_input_stock_loc_id, 100)
        bom = self.env['mrp.bom'].create({
            'product_id': finished_product.id,
            'product_tmpl_id': finished_product.product_tmpl_id.id,
            'product_qty': 1.0,
            'type': 'normal',
            'bom_line_ids': [
                (0, 0, {'product_id': component.id, 'product_qty': 1.0})
            ]})
        mo_form = Form(self.env['mrp.production'])
        mo_form.product_id = finished_product
        mo_form.bom_id = bom
        mo_form.product_qty = 5
        mo = mo_form.save()
        mo.action_confirm()
        picking = self.env['stock.picking'].search([('product_id', '=', component.id)], limit=1)

        self.assertEqual(picking.serie_transfer_document, False)
        self.assertEqual(picking.number_transfer_document, False)

        picking.picking_number = '233-1232323'
        self.assertEqual(picking.serie_transfer_document, '233')
        self.assertEqual(picking.number_transfer_document, '1232323')

        picking.picking_number = '2331232323'
        self.assertEqual(picking.serie_transfer_document, False)
        self.assertEqual(picking.number_transfer_document, False)

        print('-------------------------invoice_type_document_extension TEST OK--------------------------')
