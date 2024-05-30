from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError
from datetime import date
@tagged('post_install', 'external')
class TestPleInvBal1One(TransactionCase):

    def setUp(self):
        super(TestPleInvBal1One, self).setUp()
        self.ple_report = self.env['ple.report.inv.bal.one']
        self.date_start = date.today().replace(month=1, day=1)
        self.date_end = date.today()
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})
        self.company = self.env['res.company'].create({'name': 'Test Company'})

        self.company = self.env['res.company'].create({
            'name': 'Company for test',
        })
        print("---------------------- OK-----------------------------")
    def test_create_book_16_01(self):
        report = self.ple_report.create({
            'company_id': self.company.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'state_send': '0',
            'date_ple': date.today(),
            'financial_statements_catalog': '02',
            'eeff_presentation_opportunity': '01',
        })   
        report.create_book_16_01()
        self.assertTrue(report.xls_binary_16_01)
        self.assertTrue(report.txt_binary_16_01)
        self.assertTrue(report.pdf_binary_16_01)        
        print("---------------------- OK----------------------------")
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
        print("---------------------- OK ----------------------------")


