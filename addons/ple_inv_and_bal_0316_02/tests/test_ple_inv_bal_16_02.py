from odoo.tests.common import TransactionCase
from datetime import datetime

class TestPLEInvBal(TransactionCase):

    def setUp(self):
        super().setUp()

        self.company = self.env['res.company'].create({
            'name': 'GANEMO S.A.C.',
            'vat': '20551583041',
        })

        self.report_obj = self.env['ple.report.inv.bal.16.2']

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

        report = self.report_obj.create(vals)

        data = {
            'identification_number': 'M000000002',
            'participations_number': 420.00,
            'participations_percentage': 1.0,
        }

        report.company_id.lines_report_0316 = [(0, 0, data)]

        report.action_generate_excel()

        self.assertTrue(report.xls_binary)
        self.assertTrue(report.txt_binary)

        xls_filename_expected = 'Libro_Estructura_Accionaria_Participaciones_Sociales_202012.xlsx'
        txt_filename_expected = 'LE2055158304120201231031602010011.txt'

        self.assertEqual(report.xls_filename, xls_filename_expected)
        self.assertEqual(report.txt_filename, txt_filename_expected)
        print("---------------------- OK----------------------------")
