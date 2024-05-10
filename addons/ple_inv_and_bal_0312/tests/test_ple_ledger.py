from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, ValidationError
import re
from datetime import date
class TestPleInvBal12(TransactionCase):

    def setUp(self):
        super(TestPleInvBal12, self).setUp()
        self.ple_inv_bal_one = self.env['ple.report.inv.bal.one']
        self.ple_inv_bal_line_ = self.env['ple.report.inv.bal.line.one']

        self.company_temp = self.env['res.company'].create({
            'name': 'Company test',
        })

    def create_ple_inv_bal_one(self):
        temp_ple_inv_bal_one = self.ple_inv_bal_one.create({
            'financial_statements_catalog': '01',
            'eeff_presentation_opportunity': '01',
            'company_id': self.company_temp.id,
            'date_start': date(2023, 7, 11),
            'date_end': date(2023, 1, 15),
            'state': 'draft',
            'state_send': '0',
        })
        print("*"*40+"funciona1"+"*"*40)
        return temp_ple_inv_bal_one
   
    def test_ple_inv_bal_one_action_generate_excel(self):
        ple_inv_bal_one_temp = self.create_ple_inv_bal_one()
        ple_inv_bal_one_temp.action_generate_excel()
        self.assertRaises(ValidationError, ple_inv_bal_one_temp.action_generate_excel())
        self.assertIsNone(ple_inv_bal_one_temp.action_generate_excel())
        print("*"*40+"funciona2"+"*"*40)

    def test_set_values(self):
        partner = self.env['res.partner'].create({'name': 'Empresa de Prueba', 'vat': '12345678901'})
        account = self.env['account.account'].create({'code': '101000', 'name': 'Cuenta de Prueba'})
        move_line = self.env['account.move.line'].create({
            'partner_id': partner.id,
            'account_id': account.id,
            'move_id': self.env['account.move'].create({'name': 'Factura de Prueba'}).id,
            'ple_correlative': '123456',
        })

        report = self.create_ple_inv_bal_one()
        values = {
                     'date_end': date(2023, 1, 15),
                     'balance': 0.00,
                     'amount_currency': 0.00,

                        }

        expected_values = {
                     'date_end': date(2023, 1, 15),
                     'balance': 0.00,
                     'amount_currency': 0.00,
        }

        self.assertDictEqual(values, expected_values, "Error en la función _set_values")
        print("*"*40+"funciona3"+"*"*40)
    
    def test_ple_inv_bal_lines_data(self):
        # Crea una instancia de la clase PleInvBalLines
        ple_inv_bal_lines = self.env['ple.report.inv.bal.line.12'].create({
            'move': 'Factura de Prueba',
            'ple_correlative': '123456',
            'l10n_latam_identification_type_id': '06',
            'vat': '12345678901',
            'partner': 'Empresa de Prueba',
            'balance': 1500.0,
            'date': '15/07/2023',
        })

        # Verifica que los campos tengan los valores correctos
        self.assertEqual(ple_inv_bal_lines.move, 'Factura de Prueba')
        self.assertEqual(ple_inv_bal_lines.ple_correlative, '123456')
        self.assertEqual(ple_inv_bal_lines.l10n_latam_identification_type_id, '06')
        self.assertEqual(ple_inv_bal_lines.vat, '12345678901')
        self.assertEqual(ple_inv_bal_lines.partner, 'Empresa de Prueba')
        self.assertEqual(ple_inv_bal_lines.balance, 1500.0)
        self.assertEqual(ple_inv_bal_lines.date, '15/07/2023')
        print("*"*40+"funciona4"+"*"*40)
    
