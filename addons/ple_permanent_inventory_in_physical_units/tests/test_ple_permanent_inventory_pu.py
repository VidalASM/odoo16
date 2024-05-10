from odoo.tests import common


class TestPlePermanentInventoryPhysicalUnits(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.inventory = self.env['ple.permanent.inventory.physical.units'].create({
            'date_start': '2023-01-01',
            'company_id': self.env.ref('base.main_company').id,
            'state': 'draft',
            'state_send': '1',
            'date_start': '2021-01-01',
            'date_end': '2021-01-31',
        })

    def test_action_calc_balance(self):
        self.inventory.action_calc_balance()
        self.assertTrue(self.inventory.validation_calc_balance)

    def test_action_generate_product_list(self):
        to_date = '2023-01-01'
        data = self.inventory.action_generate_product_list(to_date)

    def test_opening_balance_units(self):
        product = self.env['product.product'].create({
            'name': 'Product Test',
        })
        quantity_hand = {
            'quantity_product_hand': 10,
            'udm_product': 'uom',
        }
        year, month, day = '2023', '01', '01'
        data = self.inventory.opening_balance_units(
            product.id, quantity_hand, year, month, day)
    print('============= Test PlePermanentInventoryPhysicalUnits OK ====================')
