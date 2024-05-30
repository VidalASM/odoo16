from odoo.tests.common import TransactionCase

import math


class TestSeparateSaleOrderInvoiceLine(TransactionCase):
    def setUp(self):
        super(TestSeparateSaleOrderInvoiceLine, self).setUp()

        self.partner = self.env["res.partner"].create(
            {
                "name": "Nombre del Partner",
                "email": "partner@example.com",
                "phone": "1234567890",
            }
        )

        self.product_1 = self.env["product.product"].create(
            {
                "name": "Producto 1",
                "invoice_policy": "order",
                "list_price": 100.0,
            }
        )

        self.product_2 = self.env["product.product"].create(
            {
                "name": "Producto 2",
                "invoice_policy": "delivery",
                "list_price": 150.0,
            }
        )

    def test_validate_separate_invoice_line_qty_integer_product_invoice_policy_order(
        self,
    ):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 5,
                            "price_unit": self.product_1.list_price,
                        },
                    ),
                ],
            }
        )
        sale_order.action_confirm()

        invoice = sale_order._create_invoices_split_sale_order_line(split=True)

        expected_lines = int(sum(line.product_uom_qty for line in sale_order.order_line))
        actual_lines = len(invoice.invoice_line_ids)

        self.assertEqual(
            actual_lines,
            expected_lines,
            "La factura no tiene la cantidad de líneas esperadas.",
        )

    def test_validate_separate_invoice_line_qty_float_product_invoice_policy_order(
        self,
    ):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 5.8,
                            "price_unit": self.product_1.list_price,
                        },
                    ),
                ],
            }
        )
        sale_order.action_confirm()

        invoice = sale_order._create_invoices_split_sale_order_line(split=True)

        sum_product_uom_qty = sum(line.product_uom_qty for line in sale_order.order_line)
        expected_lines = math.floor(sum_product_uom_qty)

        if sum_product_uom_qty > expected_lines:
            expected_lines += 1

        actual_lines = len(invoice.invoice_line_ids)

        self.assertEqual(
            actual_lines,
            expected_lines,
            "La factura no tiene la cantidad de líneas esperadas.",
        )

    def test_validate_separate_invoice_line_qty_integer_product_invoice_policy_delivery(
        self,
    ):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 4,
                            "price_unit": self.product_2.list_price,
                        },
                    ),
                ],
            }
        )
        sale_order.action_confirm()

        picking_ids = sale_order.picking_ids
        for picking in picking_ids:
            if picking.state == "draft":
                picking.action_confirm()
            picking.action_set_quantities_to_reservation()
            picking.button_validate()

        invoice = sale_order._create_invoices_split_sale_order_line(split=True)

        expected_lines = int(sum(line.qty_delivered for line in sale_order.order_line))
        actual_lines = len(invoice.invoice_line_ids)

        self.assertEqual(
            actual_lines,
            expected_lines,
            "La factura no tiene la cantidad de líneas esperadas.",
        )

    def test_validate_separate_invoice_line_qty_float_product_invoice_policy_delivery(
        self,
    ):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 4.8,
                            "price_unit": self.product_2.list_price,
                        },
                    ),
                ],
            }
        )
        sale_order.action_confirm()

        picking_ids = sale_order.picking_ids
        for picking in picking_ids:
            if picking.state == "draft":
                picking.action_confirm()
            picking.action_set_quantities_to_reservation()
            picking.button_validate()

        invoice = sale_order._create_invoices_split_sale_order_line(split=True)

        sum_qty_delivered = sum(line.qty_delivered for line in sale_order.order_line)
        expected_lines = math.floor(sum_qty_delivered)

        if sum_qty_delivered > expected_lines:
            expected_lines += 1

        actual_lines = len(invoice.invoice_line_ids)

        self.assertEqual(
            actual_lines,
            expected_lines,
            "La factura no tiene la cantidad de líneas esperadas.",
        )

    def test_validate_not_separate_invoice_line_product_invoice_policy_order(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 5,
                            "price_unit": self.product_1.list_price,
                        },
                    ),
                ],
            }
        )
        sale_order.action_confirm()

        invoice = sale_order._create_invoices_split_sale_order_line(split=False)

        expected_lines = len(sale_order.order_line)
        actual_lines = len(invoice.invoice_line_ids)

        self.assertEqual(
            actual_lines,
            expected_lines,
            "La factura no tiene la cantidad de líneas esperadas.",
        )

    def test_validate_not_separate_invoice_line_product_invoice_policy_delivery(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 4,
                            "price_unit": self.product_2.list_price,
                        },
                    ),
                ],
            }
        )
        sale_order.action_confirm()

        picking_ids = sale_order.picking_ids
        for picking in picking_ids:
            if picking.state == "draft":
                picking.action_confirm()
            picking.action_set_quantities_to_reservation()
            picking.button_validate()

        invoice = sale_order._create_invoices_split_sale_order_line(split=False)

        expected_lines = len(sale_order.order_line)
        actual_lines = len(invoice.invoice_line_ids)

        self.assertEqual(
            actual_lines,
            expected_lines,
            "La factura no tiene la cantidad de líneas esperadas.",
        )

    def test_validate_separate_invoice_line_multi_product_invoice_policy(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 5,
                            "price_unit": self.product_1.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 4,
                            "price_unit": self.product_2.list_price,
                        },
                    ),
                ],
            }
        )
        sale_order.action_confirm()

        picking_ids = sale_order.picking_ids
        for picking in picking_ids:
            if picking.state == "draft":
                picking.action_confirm()
            picking.action_set_quantities_to_reservation()
            picking.button_validate()

        invoice = sale_order._create_invoices_split_sale_order_line(split=True)

        sum_qty_product_policy_delivery = sum(
            line.qty_delivered
            for line in sale_order.order_line.filtered(
                lambda line: line.product_id.invoice_policy == "delivery"
            )
        )
        sum_qty_product_policy_order = sum(
            line.product_uom_qty
            for line in sale_order.order_line.filtered(
                lambda line: line.product_id.invoice_policy == "order"
            )
        )

        expected_lines = int(sum_qty_product_policy_delivery + sum_qty_product_policy_order)
        actual_lines = len(invoice.invoice_line_ids)

        self.assertEqual(
            actual_lines,
            expected_lines,
            "La factura no tiene la cantidad de líneas esperadas.",
        )
