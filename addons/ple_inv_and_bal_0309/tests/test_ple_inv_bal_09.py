from odoo.tests.common import TransactionCase
from datetime import date
import base64


class TestPleInvBal09(TransactionCase):
    def setUp(self):
        super(TestPleInvBal09, self).setUp()

        self.ple_model = self.env['ple.report.inv.bal.09']
        self.ple_line_model = self.env['ple.report.inv.bal.line.09']
        self.date_start = date.today().replace(month=1, day=1)
        self.date_end = date.today()
        self.company = self.env['res.company'].create({
            'name': 'Company for test',
        })

    def test_generate_data_report_309(self):
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
            'asset_intangible_id': self.env['asset.intangible'].create({
                'name': 'Activo Intangible de prueba',
                'title_code': '01'
            }).id,
        })

        ple_report = self.ple_model.create({
            'date_start': self.date_start,
            'date_end': self.date_end,
            'company_id': self.company.id,
            'state_send': '0',
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
            'xls_filename_309': 'Filaname .xls',
            'xls_binary_309': 'Reporte .XLS 3.7',
            'txt_filename_309': 'Filaname .txt',
            'txt_binary_309': 'Reporte .TXT 3.7',
            'pdf_filename_309': 'Filaname .pdf',
            'pdf_binary_309': 'Reporte .PDF 3.7',
            'line_ids_309': [(0, 0, {
                'ple_correlative': 'M000000001',
                'ple_selection': 'investment_active_intangible_3_9',
                'code_prefix_start': '13',
                'name_aml': 'Línea de prueba',
                'code_account': '1355f6',
                'date': self.date_end.strftime('%Y%m%d'),
                'balance': move_line.balance,
                'balance_amortization_xls': move_line.balance,
            })]
        })

        ple_report.generate_data_report_309()

        self.assertEqual(len(ple_report.line_ids_309), 1)

        line = ple_report.line_ids_309
        self.assertEqual(line.ple_correlative, 'M000000001')
        self.assertEqual(line.code_prefix_start,
                         move_line.account_id.group_id.code_prefix_start)
        self.assertEqual(line.name_aml, move_line.name)
        self.assertEqual(line.code_account, move_line.account_id.code)
        self.assertEqual(line.date, self.date_end.strftime('%Y%m%d'))
        self.assertEqual(line.balance, round(move_line.balance))
        self.assertEqual(line.balance_amortization_xls,
                         round(move_line.balance))

    def test_action_generate_excel(self):

        ple_report = self.ple_model.create({
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
            'date_start': self.date_start,
            'date_end': self.date_end,
            'company_id': self.company.id,
            'state_send': '0'
        })

        ple_report.action_generate_excel()

        self.assertTrue(ple_report.xls_filename_309)
        self.assertTrue(ple_report.xls_binary_309)

        self.assertTrue(ple_report.txt_filename_309)
        self.assertTrue(ple_report.txt_binary_309)

        self.assertTrue(ple_report.pdf_filename_309)
        self.assertTrue(ple_report.pdf_binary_309)

        xls_content = base64.b64decode(ple_report.xls_binary_309)
        txt_content = base64.b64decode(ple_report.txt_binary_309)
        pdf_content = base64.b64decode(ple_report.pdf_binary_309)

        self.assertTrue(xls_content)
        self.assertTrue(txt_content)
        self.assertTrue(pdf_content)
