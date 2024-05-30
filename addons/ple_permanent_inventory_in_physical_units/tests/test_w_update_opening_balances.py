from odoo.tests.common import TransactionCase


class TestUpdateOpeningWizard(TransactionCase):

    def setUp(self):
        super().setUp()
        self.UpdateOpeningWizard = self.env["update.opening.wizard"]
        self.PlePermanentInventory = self.env["ple.permanent.inventory.physical.units"]

        # Crear objetos necesarios para las pruebas

    def test_update_opening_balances(self):
        "Check update_opening_balances method"
        borrower_id = self.PlePermanentInventory.create({
            'state': 'draft',
            'state_send': '1',
            'date_start': '2021-01-01',
            'date_end': '2021-01-31',
        })
        to_id = 1
        context = {'default_permanent_id': {'default_permanent_id': to_id}}
        self.env.context = context
        wizard = self.UpdateOpeningWizard.create(
            {'borrower_id': borrower_id.id})
        wizard.update_opening_balances()

        print("Test update_opening_balances UpdateOpeningWizard OK ...... !!!!")
        print('==================== Test Update Opening Balances ====================')

    def test_update_opening_balances_2(self):
        "Check update_opening_balances_2 method"
        borrower_id = self.PlePermanentInventory.create({
            'state': 'draft',
            'state_send': '1',
            'date_start': '2021-01-01',
            'date_end': '2021-01-31',
        })
        to_id = 1
        context = {'default_permanent_id': {'default_permanent_id': to_id}}
        self.env.context = context
        wizard = self.UpdateOpeningWizard.create(
            {'borrower_id': borrower_id.id})
        wizard.update_opening_balances_2()

        print("Test update_opening_balances_2 UpdateOpeningWizard OK ...... !!!!")
        print('==================== Test Update Opening Balances 2 ====================')
