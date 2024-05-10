from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date
import re


class TestPleInvBal11(TransactionCase):

    def setUp(self):
        super(TestPleInvBal11, self).setUp()
        self.ple_inv_bal_11 = self.env['ple.report.inv.bal.one']
        self.company = self.env['res.company'].create({
            'name': 'Company for test',
        })

    def create_ple_inv_bal_11(self):
        return self.ple_inv_bal_11.create({
            'company_id': self.company.id,
            'state_send': '0',
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
            'xls_filename_311': 'Test_Excel_File',
            'txt_filename_311': 'Test_Text_File',
            'pdf_filename_311': 'Test_PDF_File',
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31)
        })

    def test_action_generate_excel(self):
        ple_inv_bal_11 = self.create_ple_inv_bal_11()

        # Llama al método que se desea probar
        ple_inv_bal_11.action_generate_excel()

        # Verifica que se haya generado correctamente el informe
        self.assertTrue(ple_inv_bal_11.xls_filename_311,
                        "No se generó el nombre del archivo Excel")
        self.assertTrue(ple_inv_bal_11.xls_binary_311,
                        "No se generó el contenido del archivo Excel")
        self.assertTrue(ple_inv_bal_11.txt_filename_311,
                        "No se generó el nombre del archivo de texto")
        self.assertTrue(ple_inv_bal_11.txt_binary_311,
                        "No se generó el contenido del archivo de texto")
        self.assertTrue(ple_inv_bal_11.pdf_filename_311,
                        "No se generó el nombre del archivo PDF")
        self.assertTrue(ple_inv_bal_11.pdf_binary_311,
                        "No se generó el contenido del archivo PDF")
        self.assertFalse(ple_inv_bal_11.line_ids_311,
                         "Las líneas del informe 3.11 no se eliminaron")
        print('------------------TEST 11 OK------------------')

    def test_generate_data_report_311(self):
        ple_inv_bal_11 = self.create_ple_inv_bal_11()

        # Llama al método para generar los datos del informe
        data = ple_inv_bal_11.generate_data_report_311()

        self.assertTrue(isinstance(data, dict), "Los datos no se generaron como se esperaba")
        print('------------------TEST 11 OK------------------')