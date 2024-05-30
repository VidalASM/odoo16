from odoo.tests.common import TransactionCase


class TestAccountAccount(TransactionCase):

    def setUp(self):
        super().setUp()
        self.AccountAccount = self.env["account.account"]
        self.account = self.AccountAccount.create({
            "name": "Account 1",
            "code": "123456",
            "ple_selection": "stock_revaluation_book"
            # Otros campos requeridos para crear la cuenta
        })
        print("SetUp Account OK ...... !!!!")

    def test_ple_selection(self):
        "Check ple_selection field"
        ple_selection = self.account.ple_selection
        self.assertEqual(ple_selection, 'stock_revaluation_book')
        print("Test ple_selection Account OK ...... !!!!")

    def test_fields_view_get(self):
        "Check fields_view_get method"
        view = self.AccountAccount.fields_view_get(view_type='form')
        self.assertIn('ple_selection', view['fields'])
        print("Test fields_view_get Account OK ...... !!!!")
        print("==================== Test AccountAccount OK ====================")


class TestProductTemplate(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ProductTemplate = self.env['product.template']
        self.product_template = self.ProductTemplate.create({
            "name": "Product 1",
            "stock_catalog": ['1', '3', '9'][0],
            "stock_type": ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10'][0]
        })
        print("SetUp ProductTemplate OK ...... !!!!")

    def test_stock_catalog(self):
        "Check stock_catalog field"
        stock_catalog = self.product_template.stock_catalog
        self.assertIn(stock_catalog, ['1', '3', '9'])
        print("Test stock_catalog ProductTemplate OK ...... !!!!")

    def test_stock_type(self):
        "Check stock_type field"
        stock_type = self.product_template.stock_type
        self.assertIn(stock_type, ['01', '02', '03',
                      '04', '05', '06', '07', '08', '09', '10'])
        print("Test stock_type ProductTemplate OK ...... !!!!")

    def test_fields_view_get(self):
        "Check fields_view_get method"
        view = self.ProductTemplate.fields_view_get(view_type='form')
        self.assertIn('stock_catalog', view['fields'])
        self.assertIn('stock_type', view['fields'])
        print("Test fields_view_get ProductTemplate OK ...... !!!!")
        print("==================== Test ProductTemplate OK ====================")


class TestStockLocation(TransactionCase):

    def setUp(self):
        super().setUp()
        self.StockLocation = self.env["stock.location"]
        self.stock_location = self.StockLocation.create({
            "name": "Location 1",
            "correlative": 123,
            # Otros campos requeridos para crear la ubicación
        })
        print("SetUp StockLocation OK ...... !!!!")

    def test_correlative(self):
        "Check correlative field"
        correlative = self.stock_location.correlative
        self.assertEqual(correlative, 123)
        print("Test correlative StockLocation OK ...... !!!!")

    def test_fields_view_get(self):
        "Check fields_view_get method"
        view = self.StockLocation.fields_view_get(view_type='form')
        self.assertIn('correlative', view['fields'])
        print("Test fields_view_get StockLocation OK ...... !!!!")
        print("==================== Test StockLocation OK ====================")


class TestStockPicking(TransactionCase):

    def setUp(self):
        super().setUp()
        self.StockPicking = self.env["stock.picking"]
        self.stock_picking = self.StockPicking.create({
            "name": "Picking 1",
            "type_operation_sunat": "01",
            "location_id": 1,
            "location_dest_id": 2,
            "picking_type_id": 1,
            # Otros campos requeridos para crear el picking
        })
        print("SetUp StockPicking OK ...... !!!!")

    def test_type_operation_sunat(self):
        "Check type_operation_sunat field"
        type_operation_sunat = self.stock_picking.type_operation_sunat
        self.assertEqual(type_operation_sunat, "01")
        print("Test type_operation_sunat StockPicking OK ...... !!!!")

    def test_onchange_type_operation_sunat(self):
        "Check onchange_type_operation_sunat method"
        self.stock_picking.onchange_type_operation_sunat()
        type_operation_sunat = self.stock_picking.type_operation_sunat
        self.assertEqual(type_operation_sunat, "02")
        print("Test onchange_type_operation_sunat StockPicking OK ...... !!!!")

    def test_check_picking_type_id_code(self):
        "Check check_picking_type_id_code method"
        location = self.env["stock.location"].create({
            "name": "Location 1",
            "usage": "internal",
            # Otros campos requeridos para crear la ubicación
        })
        code = "internal"
        flag = self.stock_picking.check_picking_type_id_code(location, code)
        self.assertTrue(flag)
        print("Test check_picking_type_id_code StockPicking OK ...... !!!!")

    def test_fields_view_get(self):
        "Check fields_view_get method"
        view = self.StockPicking.fields_view_get(view_type='form')
        self.assertIn('type_operation_sunat', view['fields'])
        print("Test fields_view_get StockPicking OK ...... !!!!")
        print("==================== Test StockPicking OK ====================")


class TestStockPickingType(TransactionCase):

    def setUp(self):
        super().setUp()
        self.StockPickingType = self.env["stock.picking.type"]
        self.stock_picking_type = self.StockPickingType.create({
            "name": "Picking Type 1",
            "ple_reason_id": "01",
            "ple_revert_id": "02",
            "sequence_code": "01",
            "code": "incoming",
            # Otros campos requeridos para crear el tipo de picking
        })
        print("SetUp StockPickingType OK ...... !!!!")

    def test_ple_reason_id(self):
        "Check ple_reason_id field"
        ple_reason_id = self.stock_picking_type.ple_reason_id
        self.assertEqual(ple_reason_id, "01")
        print("Test ple_reason_id StockPickingType OK ...... !!!!")

    def test_ple_revert_id(self):
        "Check ple_revert_id field"
        ple_revert_id = self.stock_picking_type.ple_revert_id
        self.assertEqual(ple_revert_id, "02")
        print("Test ple_revert_id StockPickingType OK ...... !!!!")

    def test_fields_view_get(self):
        "Check fields_view_get method"
        view = self.StockPickingType.fields_view_get(view_type='form')
        self.assertIn('ple_reason_id', view['fields'])
        self.assertIn('ple_revert_id', view['fields'])
        print("Test fields_view_get StockPickingType OK ...... !!!!")
        print("==================== Test StockPickingType OK ====================")

