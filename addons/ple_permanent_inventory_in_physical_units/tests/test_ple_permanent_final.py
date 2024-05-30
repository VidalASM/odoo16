from datetime import date
from odoo.tests.common import TransactionCase


class TestStockProductsValuationFinal(TransactionCase):

    def setUp(self):
        super().setUp()
        self.StockProductsValuationFinal = self.env["ple.stock.products.valuation.final"]

    def test_compute_total_value(self):
        "Check _compute_total_value method"
        quantity_product_hand = 10.0
        standard_price = 20.0
        expected_total_value = quantity_product_hand * standard_price
        product_valuation_final = self.StockProductsValuationFinal.create({
            'quantity_product_hand': quantity_product_hand,
            'standard_price': standard_price,
        })
        self.assertEqual(product_valuation_final.total_value,
                         expected_total_value)

        print("Test compute_total_value StockProductsValuationFinal OK ...... !!!!")
        print("======================== Test StockProductsValuationFinal OK ========================")


class TestPlePermanentFinal(TransactionCase):

    def setUp(self):
        super().setUp()
        self.PlePermanentFinal = self.env["ple.permanent.inventory.physical.units"]

    def test_generete_ending_balances(self):
        "Check generete_ending_balances method"
        date_start = date(2023, 1, 1)
        date_end = date(2023, 12, 31)
        company_id = 1
        inventory = self.PlePermanentFinal.create({
            'date_start': date_start,
            'date_end': date_end,
            'company_id': company_id,
            'state': 'load',
            'state_send': '1',

        })
        inventory.generete_ending_balances()

        print("Test generete_ending_balances PlePermanentFinal OK ...... !!!!")

    def test_opening_balances(self):
        "Check opening_balances method"
        product = 1
        quantity_hand = {
            'quantity_product_hand': 10.0,
            'product_valuation': 'Product A',
            'udm_product': 'uom',
            'standard_price': 20.0,
            'total_value': 200.0,
            'code_exist': 1,
        }
        year = '2023'
        month = '01'
        day = '01'
        correct_name = 'Product A'
        inventory = self.PlePermanentFinal.create({
            'state': 'draft',
            'state_send': '1',
            'date_start': '2021-01-01',
            'date_end': '2021-01-31',
        })
        inventory.opening_balances(
            product, quantity_hand, year, month, day, correct_name=correct_name
        )

        print("Test opening_balances PlePermanentFinal OK ...... !!!!")
        print('======================== Test PlePermanentFinal OK ========================')
