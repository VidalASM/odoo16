from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, ValidationError
from datetime import date

@tagged('-at_install', 'post_install')
class TestPleInvAndBal0315(TransactionCase):
    @classmethod
    def setUpClass(self):
        super(TestPleInvAndBal0315, self).setUpClass()
        self.ple_inv_bal_one = self.env['ple.report.inv.bal.one']
        self.ple_report_inv_bal_15_line = self.env['ple.report.inv.bal.line.15']

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
            # 'line_ids_315':''
        })
        return temp_ple_inv_bal_one

    def test_ple_inv_bal_one_action_generate_excel(self):
        ple_inv_bal_one_temp = self.create_ple_inv_bal_one()
        ple_inv_bal_one_temp.action_generate_excel()
        self.assertRaises(ValidationError, ple_inv_bal_one_temp.action_generate_excel())
        self.assertIsNone(ple_inv_bal_one_temp.action_generate_excel())
        print("----------------------------------TEST 1 ----------------------------------")

    def create_ple_report_inv_bal_15_line(self):
        temp_ple_report_inv_bal_15_line = self.ple_report_inv_bal_15_line.create({
            'catalog_code':'codigo prueba',
            'document_name':'nombre documento prueba',
            'name':'nombre periodo prueba',
            'accounting_seat':'CUO prueba',
            'serial_number_payment':'numero serie prueba',
            'related_payment_voucher':'voucher relacionado prueba',
            'correlative':'correlativo prueba',
            'ref':'referencia factura prueba',
            'type_l10n_latam_identification':'tipo de comprobante de pago prueba',
            'code':'codigo prueba',
            'additions':1500.0,
            'deductions':1300.0,
            'outstanding_balance':1500.0,
            'free_field':'campo libre prueba',
            # 'ple_report_inv_val_15_id':'',
        })
        return temp_ple_report_inv_bal_15_line

    def test_ple_report_inv_bal_15_generate_excel(self):
        ple_report_inv_bal_one = self.create_ple_inv_bal_one()
        ple_report_inv_bal_15_line_temp = self.create_ple_report_inv_bal_15_line()

        ple_report_inv_bal_one.write({'line_ids_315': [(6, 0, [ple_report_inv_bal_15_line_temp.id])]})

        ple_report_inv_bal_one.action_generate_excel()

        self.assertRaises(ValidationError, ple_report_inv_bal_one.action_generate_excel())
        self.assertIsNone(ple_report_inv_bal_one.action_generate_excel())

        self.assertEqual(ple_report_inv_bal_one.pdf_filename_315, f"Libro_Activos_Pasivos_Diferidos_{ple_report_inv_bal_one.date_end.strftime('%Y%m')}.pdf")
        self.assertEqual(ple_report_inv_bal_one.xls_filename_315, f"Libro_Activos_Pasivos_Diferidos_{ple_report_inv_bal_one.date_end.strftime('%Y%m')}.xlsx")
        print("----------------------------------TEST 2 ----------------------------------")