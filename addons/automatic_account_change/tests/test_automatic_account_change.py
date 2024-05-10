from odoo.tests.common import TransactionCase
from datetime import date

dat = date.today()


class TestAutomaticAccountChange(TransactionCase):
    def setUp(self):
        super(TestAutomaticAccountChange, self).setUp()
        self.model_move = self.env['account.move']
        self.currency_id_pen = self.env['res.currency'].search([
            ('name', '=', 'PEN')
        ])
        self.currency_id_usd = self.env['res.currency'].search([
            ('name', '=', 'USD')
        ])
        self.account_model = self.env['account.account']
        self.account_model_type = self.env['account.account.type'].create({
            'name': 'account',
            'type': 'other',
            'internal_group': 'equity',
        })

        self.journal_id_usd = self.env['account.journal'].create({
            'name': 'Diario Venta',
            'type': 'sale',
            'code': 'TestD',
            'currency_id': self.currency_id_usd.id,
        })

        self.acc_vent = self.account_model.create({
            'name': 'venta',
            'code': '1224',
            'user_type_id': self.account_model_type.id,
            'company_id': self.env.ref("base.main_company").id,
        })

        self.acc_purch = self.account_model.create({
            'name': 'compra',
            'code': '1223',
            'user_type_id': self.account_model_type.id,
            'company_id': self.env.ref("base.main_company").id,
        })

    def test_01_automatic_account_change(self):
        doc = self.env['account.change.by.type'].create({
            'journal_id': self.journal_id_usd.id,
            'currency_id': self.currency_id_usd.id,
            'sale_account_id': self.acc_vent.id,
            'purchase_account_id': self.acc_purch.id,
            'company_id': self.env.ref("base.main_company").id,
        })
        self.assertTrue(doc)
        print('--------TEST -Cambio de cuenta- OK-------')

    def test_02_automatic_account_change(self):
        doc = self.model_move.create({
            'date': dat,
            'state': 'draft',
            'move_type': 'entry',
            'company_id': self.env.ref("base.main_company").id,
            'journal_id': self.journal_id_usd.id,
            'currency_id': self.currency_id_usd.id,
            'pay_sell_force_account_id': self.acc_vent.id,
        })
        self.assertTrue(doc)
        print('--------TEST -Cuenta por cobrar- OK-------')
