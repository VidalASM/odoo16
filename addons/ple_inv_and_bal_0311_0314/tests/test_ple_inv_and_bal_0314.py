from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date
import re


class TestPleInvBal14(TransactionCase):

    def setUp(self):
        super(TestPleInvBal14, self).setUp()
        self.ple_inv_bal_14 = self.env['ple.report.inv.bal.one']
        self.company = self.env['res.company'].create({
            'name': 'Company for test',
        })

    def create_ple_inv_bal_14(self):
        return self.ple_inv_bal_14.create({
            'company_id': self.company.id,
            'state_send': '0',
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
            'xls_filename_314': 'Test_Excel_File',
            'txt_filename_314': 'Test_Text_File',
            'pdf_filename_314': 'Test_PDF_File',
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31)
        })

    def test_action_generate_excel(self):
        ple_inv_bal_14 = self.create_ple_inv_bal_14()

        # Llama al método que se desea probar
        ple_inv_bal_14.action_generate_excel()

        # Verifica que se haya generado correctamente el informe
        self.assertTrue(ple_inv_bal_14.xls_filename_314,
                        "No se generó el nombre del archivo Excel")
        self.assertTrue(ple_inv_bal_14.xls_binary_314,
                        "No se generó el contenido del archivo Excel")
        self.assertTrue(ple_inv_bal_14.txt_filename_314,
                        "No se generó el nombre del archivo de texto")
        self.assertTrue(ple_inv_bal_14.txt_binary_314,
                        "No se generó el contenido del archivo de texto")
        self.assertTrue(ple_inv_bal_14.pdf_filename_314,
                        "No se generó el nombre del archivo PDF")
        self.assertTrue(ple_inv_bal_14.pdf_binary_314,
                        "No se generó el contenido del archivo PDF")
        self.assertFalse(ple_inv_bal_14.line_ids_314,
                         "Las líneas del informe 3.14 no se eliminaron")
        print('------------------TEST 14 OK------------------')

    def test_generate_data_report_314(self):
        ple_inv_bal_14 = self.create_ple_inv_bal_14()

        # Llama al método para generar los datos del informe
        data = ple_inv_bal_14.generate_data_report_314()

        self.assertTrue(isinstance(data, dict), "Los datos no se generaron como se esperaba")
        print('------------------TEST 14 OK------------------')
