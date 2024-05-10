from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, ValidationError
from datetime import date

@tagged('-at_install', 'post_install')
class TestPleInvAndBal0304(TransactionCase):

    @classmethod
    def setUpClass(self):
        super(TestPleInvAndBal0304, self).setUpClass()
        self.ple_inv_bal_one = self.env['ple.report.inv.bal.one']
        self.ple_report_inv_bal_04 = self.env['ple.report.inv.bal.04']
        self.ple_report_inv_bal_04_line = self.env['ple.report.inv.bal.line.04']

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
        return temp_ple_inv_bal_one

    def test_ple_inv_bal_one_action_generate_excel(self):
        ple_inv_bal_one_temp = self.create_ple_inv_bal_one()
        ple_inv_bal_one_temp.action_generate_excel()
        self.assertRaises(ValidationError, ple_inv_bal_one_temp.action_generate_excel())
        self.assertIsNone(ple_inv_bal_one_temp.action_generate_excel())
        print("----------------------------------TEST 1 ----------------------------------")

    def create_ple_report_inv_bal_04(self):
        temp_ple_report_inv_bal_04 = self.ple_report_inv_bal_04.create({
            'company_id': self.company_temp.id,
            'date_start': date(2023, 7, 11),
            'date_end': date(2023, 8, 15),
            'state': 'draft',
            'state_send': '0',
            'date_ple': date(2023, 8, 15),
            'financial_statements_catalog': '01',
            'eeff_presentation_opportunity': '01',
        })
        return temp_ple_report_inv_bal_04

    def create_ple_report_inv_bal_04_line(self):
        temp_ple_report_inv_bal_04_line = self.ple_report_inv_bal_04_line.create({
            'period':'periodo prueba',
            'code_uo':'2356',
            'correlative':'5436',
            'doc_type':'ruc',
            'doc_num':'123456789',
            'name_client':'Juan Perez',
            'date_ref':'fecha prueba',
            'mont': 1500.0,
            'status':'Activo',
            'note':'Nota prueba',
            'account':23.45,
            'desc_account':'desc cuenta prueba',
            'valor':1000.0,
            'sequence':1.0,
        })
        return temp_ple_report_inv_bal_04_line

    def test_ple_report_inv_bal_04_action_generate_excel(self):
        ple_report_inv_bal_04_temp = self.create_ple_report_inv_bal_04()
        ple_report_inv_bal_04_line_temp = self.create_ple_report_inv_bal_04_line()

        ple_report_inv_bal_04_temp.write({'line_ids': [(6, 0, ple_report_inv_bal_04_line_temp.ids)]})
        ple_report_inv_bal_04_line_temp.write({'ple_report_inv_val_04_id': ple_report_inv_bal_04_temp.id})

        ple_report_inv_bal_04_temp.action_generate_excel()
        year, month, day = ple_report_inv_bal_04_temp.date_end.strftime('%Y/%m/%d').split('/')

        self.assertRaises(ValidationError, ple_report_inv_bal_04_temp.action_generate_excel())
        self.assertIsNone(ple_report_inv_bal_04_temp.action_generate_excel())

        self.assertEqual(ple_report_inv_bal_04_temp.xls_filename, f'Libro_Ctas. por cobrar: Trab. Soc. Direc. Ger. Acc._{year}{month}.xlsx')
        self.assertEqual(ple_report_inv_bal_04_temp.pdf_filename, f'Libro_Cuentas por cobrar Acc. y Pers_{year}{month}.pdf')
        print("----------------------------------TEST 2 ----------------------------------")