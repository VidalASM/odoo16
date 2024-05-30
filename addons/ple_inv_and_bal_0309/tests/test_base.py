from datetime import date
from odoo.tests.common import TransactionCase


class TestInventoryAndBalances09(TransactionCase):
    def setUp(self):
        super(TestInventoryAndBalances09, self).setUp()

        # Crear instancias necesarias para las pruebas
        self.account_model = self.env['account.account']
        self.move_model = self.env['account.move']
        self.move_line_model = self.env['account.move.line']
        self.inventory_model = self.env['inventory.and.balances.09']
        self.journal_model = self.env['account.journal']
        self.account = self.account_model.create({
            'name': 'Cuenta de Prueba',
            'code': '1355f6',
            'reconcile': True,
        })
        self.journal = self.journal_model.create({
            'name': 'Diario de Prueba',
            'type': 'bank',
            'code': '1355f6',
        })

        self.move = self.move_model.create({
            'state': 'draft',
            'journal_id': self.journal.id,
        })
        self.move_line = self.move_line_model.create({
            'name': 'Línea de Débito de Prueba',
            'move_id': self.move.id,
            'account_id': self.account.id,
        })

    def test_onchange_accounting_seat_09(self):
        inventory = self.inventory_model.create({
            'accounting_seat_09': self.move_line.id,
        })

        inventory.onchange_accounting_seat_09()
        self.assertEqual(inventory.provision_account_09, self.account)
        self.assertEqual(inventory.account_date_ple_09, self.move.date)
        self.assertEqual(inventory.amount_balance_09,
                         self.move_line.balance)
