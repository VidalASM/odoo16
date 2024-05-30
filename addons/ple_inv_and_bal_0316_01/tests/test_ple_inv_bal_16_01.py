from odoo.tests.common import TransactionCase
from datetime import date
import base64

class TestPleInvBal0316(TransactionCase):

    def setUp(self):
        super(TestPleInvBal0316, self).setUp()       
        self.ple_report = self.env['ple.report.inv.bal.16.1']     
        self.ple_report_line = self.env['ple.report.inv.bal.line.16.1']
        self.date_start = date.today().replace(month=1, day=1)
        self.date_end = date.today()
        self.company = self.env['res.company'].create({
            'name': 'Company for test',
        })
        print("---------------------- OK-----------------------------")
    def test_set_values_method(self):
        partner = self.env['res.partner'].create({'name': 'Test Partner'})
        move = self.env['account.move'].create({'name': 'Test Move'})
        account = self.env['account.account'].create({'name': 'Test Account','code': '234567'})
        obj_move_line = self.env['account.move.line'].create({
            'partner_id': partner.id,
            'move_id': move.id,
            'name': 'Test Name',
            'currency_id': self.env.ref('base.USD').id,
            'account_id': account.id,
            'date_maturity': '2023-08-08',
            'ple_correlative': 'Test Correlative',
        })     
        values = self.ple_report._set_values(obj_move_line)     
        expected_values = {
            'partner': partner.name,
            'move': move.name,
            'name': 'Test Name',
            'ref': '',
            'name_currency': 'USD',
            'account_currency': '', 
            'date_maturity':  date(2023, 8, 8),
            'vat': '0',
            'ple_correlative': 'Test Correlative',
            'l10n_latam_identification_type_id': '0',  
        }
        self.assertEqual(values, expected_values)   
        print("----------------------TEST OK-----------------------------")

    def test_generate_data(self):
        move_line = self.env['account.move.line'].create({
            'name': 'Línea de prueba',
            'move_id': self.env['account.move'].create({
                'name': 'Asiento de prueba',
                'date': self.date_end,
            }).id,
            'account_id': self.env['account.account'].create({
                'name': 'Cuenta de prueba',
                'code': '1355f6',
                'reconcile': True,
            }).id,         
        })   
        report = self.ple_report.create({
            'date_start': self.date_start,
            'date_end': self.date_end,
            'company_id': self.company.id,
            'state_send': '0',
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',           
        })
        report.generate_data()
        self.assertEqual(len(report.state_send), 1)
        print("---------------------- OK-----------------------------")
    def test_action_generate_excel(self):
        report = self.ple_report.create({
           'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
            'date_start': self.date_start,
            'date_end': self.date_end,
            'company_id': self.company.id,
            'state_send': '0'
        })
        report.action_generate_excel()
        self.assertTrue(report.xls_binary)
        self.assertTrue(report.txt_binary)
        self.assertTrue(report.pdf_binary)
        print("---------------------- OK-----------------------------")
    def test_create_ple_inv_bal_line(self):        
        report = self.ple_report.create({
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
            'date_start': self.date_start,
            'date_end': self.date_end,
            'company_id': self.company.id,
            'state_send': '0'
        })
        report_line = self.ple_report_line.create({
            'balance': 123,  
            'report_id': report.id,
        })
        self.assertEqual(report_line.balance, 123)       
        self.assertEqual(report_line.report_id.id, report.id)
        print("---------------------- OK-----------------------------")