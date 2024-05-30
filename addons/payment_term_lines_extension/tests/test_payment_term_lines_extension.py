from odoo import fields
from odoo.tests.common import TransactionCase
from datetime import datetime
from odoo.tools import float_compare


class TestPaymentTermExtension(TransactionCase):
    def setUp(self):
        super(TestPaymentTermExtension, self).setUp()
        self.payment_term = self.env['account.payment.term'].create({
            'name': 'Test Payment Term',
        })

    def test_compute_payment_term(self):
        value = 1000.0
        currency = self.env['res.currency'].create({
            'name': 'Test Currency',
            'symbol': '$',
            'rounding': 0.01,
            'decimal_places': 2,
        })
        date_ref = fields.Date.today()
        line1 = self.env['account.payment.term.line'].create({
            'value': 'fixed',
            'value_amount': 500.0,
            'payment_id': self.payment_term.id,
        })
        line2 = self.env['account.payment.term.line'].create({
            'value': 'percent',
            'value_amount': 50.0,
            'factor_round': 1.0,
            'payment_id': self.payment_term.id,
        })
        balance_line = self.env['account.payment.term.line'].create({
            'value': 'balance',
            'days': 0,
            'payment_id': self.payment_term.id,

        })
        self.payment_term.write({'line_ids': [(6, 0, [line1.id, line2.id, balance_line.id])]})
        print('---------------------------------------VERIFY LINES OK---------------------------------------')
        # Test payment term computation
        result = self.payment_term.compute(value, date_ref=date_ref, currency=currency)
        self.assertAlmostEqual(result[0][1], 500.0, places=2)
        self.assertAlmostEqual(result[1][1], 500.0, places=2)
        print('---------------------------------------TEST RESULT OK---------------------------------------')
