from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, ValidationError
from datetime import date

@tagged('-at_install', 'post_install')
class TestPleInvAndBal0308(TransactionCase):

    @classmethod
    def setUpClass(self):
        super(TestPleInvAndBal0308, self).setUpClass()
        self.ple_inv_bal_one = self.env['ple.report.inv.bal.one']
        self.report_inv_bal_08 = self.env['ple.report.inv.bal.08']
        self.report_inv_bal_line_08 = self.env['ple.report.inv.bal.line.08']

        self.company_temp = self.env['res.company'].create({
            'name': 'Company test',
        })

        self.ple_inv_bal_line_initial_balances = self.env['ple.inv.bal.line.initial.balances.08']
        self.ple_inv_bal_line_final_balances = self.env['ple.inv.bal.line.final.balances.08']


    def create_ple_inv_bal_08(self):
        temp_ple_inv_bal_08 = self.report_inv_bal_08.create({
            'financial_statements_catalog': '01',
            'eeff_presentation_opportunity': '01',
            'company_id': self.company_temp.id,
            'date_start': date(2023, 7, 11),
            'date_end': date(2023, 1, 15),
            'state': 'draft',
            'state_send': '0',
            # 'line_ids': 'ple.report.inv.bal.line.08' one2many
        })
        return temp_ple_inv_bal_08

    def create_ple_inv_bal_line_08(self):
        temp_ple_inv_bal_line_08 = self.report_inv_bal_line_08.create({
            'name': 'test',
            'partner_id': 1,
            'camp_id': 'id_test',
            'state': 'activo',
            'catalog_code': '01',
            'document_name': 'documento test',
            'correlative': 'correlativo test',
            'type_document_transmitter': 1,
            'number_document_transmitter':'numero documento transmisor test',
            'transmitter_name':'razon social test',
            'title_code':'codigo test',
            'ple_selection':'ple selection test',
            'title_unit_value': 1500,
            'total_amount_value':'1500',
            'total_title_costs':'1500.00',
            'total_title_provision': 1600.00,
            'transmitter_name':'razon social test',
            'free_camp':'campo libre test',
            # 'ple_report_inv_bal_08_id': 'ple.report.inv.bal.08' many2one
        })
        return temp_ple_inv_bal_line_08

    def create_ple_inv_bal_one(self):
        temp_ple_inv_bal_one = self.ple_inv_bal_one.create({
            'financial_statements_catalog': '01',
            'eeff_presentation_opportunity': '01',
            'company_id': self.company_temp.id,
            'date_start': date(2023, 7, 11),
            'date_end': date(2023, 1, 15),
            'state': 'draft',
            'state_send': '0',
            # 'm2o_ple_report_inv_bal_08': 'ple.report.inv.bal.08' many2one
        })
        return temp_ple_inv_bal_one

    def test_ple_report_inv_bal_08(self):
        temp_ple_inv_bal_08 = self.create_ple_inv_bal_08()
        temp_ple_inv_bal_line_08 = self.create_ple_inv_bal_line_08()

        temp_ple_inv_bal_08.write({'line_ids': [(6, 0, temp_ple_inv_bal_line_08.ids)]})
        temp_ple_inv_bal_line_08.write({'ple_report_inv_val_08_id': temp_ple_inv_bal_08.id})


        temp_ple_inv_bal_08.action_generate_excel()
        year, month, day = temp_ple_inv_bal_08.date_end.strftime('%Y/%m/%d').split('/')

        self.assertRaises(AccessError, temp_ple_inv_bal_08.action_generate_excel())
        self.assertRaises(ValidationError, temp_ple_inv_bal_08.action_generate_excel())
        self.assertEqual(temp_ple_inv_bal_08.pdf_filename, f'Libro_Inversiones Mobiliarias_{year}{month}.pdf')
        print("----------------------------------TEST 1 Parte 1 ----------------------------------")

        temp_ple_inv_bal_one = self.create_ple_inv_bal_one()
        temp_ple_inv_bal_line_initial_balances = self.create_initial_balances()
        temp_ple_inv_bal_line_final_balances = self.create_final_balances()

        temp_ple_inv_bal_08.write({'line_initial_ids': [(6, 0, temp_ple_inv_bal_line_initial_balances.ids)]})
        temp_ple_inv_bal_08.write({'line_final_ids': [(6, 0, temp_ple_inv_bal_line_final_balances.ids)]})

        temp_ple_inv_bal_line_initial_balances.write({'ple_report_inv_val_id': temp_ple_inv_bal_08.id})
        temp_ple_inv_bal_line_final_balances.write({
            'ple_report_inv_val_id': temp_ple_inv_bal_08.id,
            'ple_report_inv_val_08_id': temp_ple_inv_bal_08.id,
        })

        temp_ple_inv_bal_one.write({'m2o_ple_report_inv_bal_08': temp_ple_inv_bal_08.id})
        self.assertRaises(AccessError, temp_ple_inv_bal_one.action_generate_excel())
        self.assertRaises(ValidationError, temp_ple_inv_bal_one.action_generate_excel())
        print("----------------------------------TEST 1 Parte 2 ----------------------------------")


    def create_initial_balances(self):
        temp_ple_inv_bal_line_initial_balances = self.ple_inv_bal_line_initial_balances.create({
            'name': 'test',
            'partner_id': 1,
            'camp_id': 'id_test',
            'state': 'activo',
            'catalog_code': '01',
            'document_name': 'documento test',
            'correlative': 'correlativo test',
            'type_document_transmitter': 1,
            'number_document_transmitter':'numero documento transmisor test',
            'transmitter_name':'razon social test',
            'title_code':'codigo test',
            'title_unit_value': 1500,
            'total_amount_value':'1500',
            'total_title_costs':'1500.00',
            'total_title_provision': 1600.00,
            'free_camp':'campo libre test',
            # 'ple_report_inv_val_idv': 'ple.report.inv.bal.08'; many2one
        })
        return temp_ple_inv_bal_line_initial_balances

    def create_final_balances(self):
        temp_ple_inv_bal_line_final_balances = self.ple_inv_bal_line_final_balances.create({
            'name': 'test',
            'camp_id': 'id_test',
            'state': 'activo',
            'catalog_code': '01',
            'document_name': 'documento test',
            'correlative': 'correlativo test',
            'type_document_transmitter': 1,
            'number_document_transmitter':'numero documento transmisor test',
            'transmitter_name':'razon social test',
            'title_code':'codigo test',
            'title_unit_value': 1500,
            'total_amount_value':'1500',
            'total_title_costs':'1500.00',
            'total_title_provision': 1600.00,
            'transmitter_name':'razon social test',
            'free_camp':'campo libre test',
            # 'ple_report_inv_val_id': 'ple.report.inv.bal.08',
            # 'ple_report_inv_val_08_id': 'ple.report.inv.bal.08',
        })
        return temp_ple_inv_bal_line_final_balances