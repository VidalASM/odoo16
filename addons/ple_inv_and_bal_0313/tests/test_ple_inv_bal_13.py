from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date
import re


class TestPleInvBal13(TransactionCase):

    def setUp(self):
        super(TestPleInvBal13, self).setUp()
        self.ple_inv_bal_one = self.env['ple.report.inv.bal.one']
        self.company = self.env['res.company'].create({
            'name': 'Company for test',
        })

    def create_ple_inv_bal_one(self):
        return self.ple_inv_bal_one.create({
            'company_id': self.company.id,
            'state_send': '0',
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
            'xls_filename_313': 'Test_Excel_File',
            'txt_filename_313': 'Test_Text_File',
            'pdf_filename_313': 'Test_PDF_File',
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
            # Agrega aquí los campos necesarios para completar el registro de prueba
        })

    def test_action_generate_excel(self):
        ple_inv_bal_one = self.create_ple_inv_bal_one()

        # Llama al método que se desea probar
        ple_inv_bal_one.action_generate_excel()

        # Verifica que se haya generado correctamente el informe
        self.assertTrue(ple_inv_bal_one.xls_filename_313,
                        "No se generó el nombre del archivo Excel")
        self.assertTrue(ple_inv_bal_one.xls_binary_313,
                        "No se generó el contenido del archivo Excel")
        self.assertTrue(ple_inv_bal_one.txt_filename_313,
                        "No se generó el nombre del archivo de texto")
        self.assertTrue(ple_inv_bal_one.txt_binary_313,
                        "No se generó el contenido del archivo de texto")
        self.assertTrue(ple_inv_bal_one.pdf_filename_313,
                        "No se generó el nombre del archivo PDF")
        self.assertTrue(ple_inv_bal_one.pdf_binary_313,
                        "No se generó el contenido del archivo PDF")
        self.assertFalse(ple_inv_bal_one.line_ids_313,
                         "Las líneas del informe 3.13 no se eliminaron")
