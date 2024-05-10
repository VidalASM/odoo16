from odoo.tests.common import TransactionCase
from datetime import datetime

class TestPLEInvBal1One(TransactionCase):

    def setUp(self):
        super().setUp()

        self.company = self.env['res.company'].create({
            'name': 'GANEMO S.A.C.',
            'vat': '20551583041',
        })

        self.inv_bal_16_2_obj = self.env['ple.report.inv.bal.16.2']
        self.inv_bal_one_obj = self.env['ple.report.inv.bal.one']

    def test_create_book_16_02(self):
        vals = {
            'company_id': self.company.id,
            'date_start': datetime.strptime('2020-09-16', '%Y-%m-%d'),
            'date_end': datetime.strptime('2020-12-31', '%Y-%m-%d'),
            'state_send': '0',
            'date_ple': datetime.now(),
            'financial_statements_catalog': '06',
            'eeff_presentation_opportunity': '01',
        }

        report_16_2 = self.inv_bal_16_2_obj.create(vals)

        vals_1_one = {
            'company_id': self.company.id,
            'date_start': datetime.strptime('2020-09-16', '%Y-%m-%d'),
            'date_end': datetime.strptime('2020-12-31', '%Y-%m-%d'),
            'state_send': '0',
            'date_ple': datetime.now(),
            'financial_statements_catalog': '06',
            'eeff_presentation_opportunity': '01',
            'm2o_ple_report_inv_bal_16_02': report_16_2.id,
        }

        report_one = self.inv_bal_one_obj.create(vals_1_one)

        report_one.create_book_16_02()

        self.assertTrue(report_one.xls_binary_16_02)
        self.assertTrue(report_one.txt_binary_16_02)

        self.assertFalse(report_one.m2o_ple_report_inv_bal_16_02.exists(), "Report 16.2 unlinked")
        print("---------------------- OK----------------------------")

    def test_action_generate_excel(self):
        vals = {
            'company_id': self.company.id,
            'date_start': datetime.strptime('2020-09-16', '%Y-%m-%d'),
            'date_end': datetime.strptime('2020-12-31', '%Y-%m-%d'),
            'state_send': '0',
            'date_ple': datetime.now(),
            'financial_statements_catalog': '06',
            'eeff_presentation_opportunity': '01',
        }

        report_16_2 = self.inv_bal_16_2_obj.create(vals)

        vals_1_one = {
            'company_id': self.company.id,
            'date_start': datetime.strptime('2020-09-16', '%Y-%m-%d'),
            'date_end': datetime.strptime('2020-12-31', '%Y-%m-%d'),
            'state_send': '0',
            'date_ple': datetime.now(),
            'financial_statements_catalog': '06',
            'eeff_presentation_opportunity': '01',
            'm2o_ple_report_inv_bal_16_02': report_16_2.id,
        }

        report_one = self.inv_bal_one_obj.create(vals_1_one)

        report_one.action_generate_excel()

        self.assertTrue(report_one.xls_binary)
        self.assertTrue(report_one.txt_binary)
        print("---------------------- OK----------------------------")

