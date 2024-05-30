from odoo.tests.common import TransactionCase


class TestStockProductsValuation(TransactionCase):

    def setUp(self):
        super().setUp()
        self.StockProductsValuation = self.env["ple.stock.products.valuation"]

    def test_compute_total_value(self):
        "Check _compute_total_value method"
        quantity_product_hand = 10.0
        standard_price = 20.0
        expected_total_value = quantity_product_hand * standard_price
        product_valuation = self.StockProductsValuation.create({
            'quantity_product_hand': quantity_product_hand,
            'standard_price': standard_price,
        })
        self.assertEqual(product_valuation.total_value, expected_total_value)

        print("Test compute_total_value StockProductsValuation OK ...... !!!!")
        print('============= Test StockProductsValuation OK ====================')
