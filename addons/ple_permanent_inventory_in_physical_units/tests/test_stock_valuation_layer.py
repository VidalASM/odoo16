from odoo.tests.common import TransactionCase


class TestStockValuationLayer(TransactionCase):

    def setUp(self):
        super().setUp()
        self.StockValuationLayer = self.env["stock.valuation.layer"]

    def test_sunat_operation_type(self):
        "Check sunat_operation_type field"

        sunat_operation_type = "01"
        valuation_layer = self.StockValuationLayer.create(
            {'sunat_operation_type': sunat_operation_type,
             'company_id': 1,
             'product_id': 1, })

        self.assertEqual(valuation_layer.sunat_operation_type,
                         sunat_operation_type)
        print("Test sunat_operation_type StockValuationLayer OK ...... !!!!")

    def test_account_move_id(self):
        "Check account_move_id field"
        account_move_id = 1

        valuation_layer = self.StockValuationLayer.create(
            {'account_move_id': account_move_id,
             'company_id': 1,
             'product_id': 1, })
        self.assertEqual(valuation_layer.account_move_id.id, account_move_id)

        print("Test account_move_id StockValuationLayer OK ...... !!!!")
