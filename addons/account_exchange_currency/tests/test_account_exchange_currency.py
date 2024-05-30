from odoo.tests.common import TransactionCase
from odoo.tests.common import Form
from datetime import datetime


class TestAccountExchangeCurrency(TransactionCase):

    def setUp(self):
        super(TestAccountExchangeCurrency, self).setUp()
        self.currency_usd = self.env['res.currency'].search([('name', '=', 'USD')])

    def test_01_validate_refund(self):
        date = datetime.now()
        currency_rate = self.env['res.currency.rate'].create({
            'name': date,
            'company_id': self.env.ref("base.main_company").id,
            'currency_id': self.currency_usd.id,
            'rate': 0.274040306094
        })

        account_form = Form(self.env['account.move'])
        val_pen = account_form.exchange_rate
        val_pen = round(val_pen / currency_rate.rate, 6)

        account_form.currency_id = self.currency_usd
        val_usd = account_form.exchange_rate

        self.assertEqual(val_pen, val_usd)
        print('----------------Ok Exchange----------------')
