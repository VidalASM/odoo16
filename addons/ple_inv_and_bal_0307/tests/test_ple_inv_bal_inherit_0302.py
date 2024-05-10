from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, Form, SavepointCase
from odoo.exceptions import AccessError
from datetime import date

@tagged('-at_install', 'post_install')
class TestPleInvAndBal0307(TransactionCase):

    @classmethod
    def setUpClass(self):
        super(TestPleInvAndBal0307, self).setUpClass()
        self.ple_inv_bal_one = self.env['ple.report.inv.bal.one']
        self.ple_inv_bal_line_one = self.env['ple.report.inv.bal.line.one']

        self.company_temp = self.env['res.company'].create({
            'name': 'Company test',
        })

        self.ple_inv_bal_one_line_initial_balances = self.env['ple.inv.bal.one.line.initial.balances']

        self.ple_inb_bal_one_line_final_balances = self.env['ple.inv.bal.one.line.final.balances']
        self.random_set = {'a': '123456', 'b': '567789', 'c':'135356', 'd': '1eg3456', 'e': '567789', 'f':'1355f6'}

    def create_accounts(self, order, order2):
        account_test = self.env['account.account'].create(
            {'name': 'Receivable', 'code': self.random_set[order], 'reconcile': True})
        journal_test = self.env['account.journal'].create({'name': 'journal test', 'type': 'bank', 'code': order2})
        account_move_test = self.env['account.move'].create(
            {'state': 'draft', 'journal_id': journal_test.id})
        account_move_line_test = self.env['account.move.line'].create({
            'name': 'account move line test',
            'move_id': account_move_test.id,
            'account_id': account_test.id,
        })
        return account_move_line_test

    def common_create_object(self, order, order2):
        account_move_line_test = self.create_accounts(order, order2)
        common_obj = {
            'period': 'Periodo prueba',
            'accounting_account': 'Cuenta contable prueba',
            'bank_account_name': 'Cuenta bancaria prueba',
            'type_currency': 'Moneda prueba',
            'balance': 1500.0,
            'status': 'Estado prueba',
            'note': 'Nota prueba',
            'bic': 'Codigo entidad financiera prueba',
            'account_bank_code': 'Número de cuenta de entidad financiera prueba',
            'sequence': 3,
            'account_ids': [(6, 0, account_move_line_test.ids)]
        }
        return common_obj

    def create_ple_inv_bal_one(self):
        temp_ple_inv_bal_one = self.ple_inv_bal_one.create({
            'financial_statements_catalog': '01',
            'eeff_presentation_opportunity': '01',
            'company_id': self.company_temp.id,
            'date_start': date(2023, 7, 11),
            'date_end': date(2023, 1, 15),
            'state': 'draft',
            'state_send': '0',
            'xls_filename_07' : 'Filaname .xls',
            'xls_binary_07'   : 'Reporte .XLS 3.7',
            'txt_filename_07' : 'Filaname .txt',
            'txt_binary_07'   : 'Reporte .TXT 3.7',
            'pdf_filename_07' : 'Filaname .pdf',
            'pdf_binary_07'   : 'Reporte .PDF 3.7',
        })
        return temp_ple_inv_bal_one

    def create_ple_inv_bal_line_one(self):
        common_obj = self.common_create_object('a', 'd')

        temp_ple_inv_bal_line_one = self.ple_inv_bal_line_one.create(common_obj)
        return temp_ple_inv_bal_line_one


    def test_ple_report_inv_val_one_id(self):

        ple_inv_bal_one_temp = self.create_ple_inv_bal_one()
        inv_bal_line_temp = self.create_ple_inv_bal_line_one()

        ple_inv_bal_one_temp.write({'line_ids': [(6, 0, inv_bal_line_temp.ids)]})
        inv_bal_line_temp.write({'ple_report_inv_val_one_id': ple_inv_bal_one_temp.id})

        ple_inv_bal_one_temp.action_generate_excel()
        year, month, day = ple_inv_bal_one_temp.date_end.strftime('%Y/%m/%d').split('/')

        self.assertRaises(AccessError, ple_inv_bal_one_temp.action_generate_excel())

        self.assertEqual(ple_inv_bal_one_temp.xls_filename, f'Libro_Efectivo y Equivalente de efectivo_{year}{month}.xlsx')
        self.assertEqual(ple_inv_bal_one_temp.pdf_filename, f'Libro_Efectivo y equivalente de efectivo_{year}{month}.pdf')

        print("---------------------------------------------TEST 1---------------------------------------------")

    def create_initial_balances(self):
        common_obj = self.common_create_object('b', 'e')
        temp_ple_initial_balances = self.ple_inv_bal_one_line_initial_balances.create(common_obj)
        return temp_ple_initial_balances

    def create_final_balances(self):
        common_obj = self.common_create_object('c', 'f')
        temp_ple_final_balances = self.ple_inb_bal_one_line_final_balances.create(common_obj)
        return temp_ple_final_balances

    def test_ple_report_inv_val_one_balances(self):
        ple_inv_bal_one_temp = self.create_ple_inv_bal_one()
        inv_bal_line_temp = self.create_ple_inv_bal_line_one()

        ple_inv_bal_one_temp.write({'line_ids': [(6, 0, inv_bal_line_temp.ids)]})
        inv_bal_line_temp.write({'ple_report_inv_val_one_id': ple_inv_bal_one_temp.id})

        ple_inv_initial_balances = self.create_initial_balances()
        ple_inv_final_balances = self.create_final_balances()

        ple_inv_bal_one_temp.write({'line_initial_ids': [(6, 0, ple_inv_initial_balances.ids)]})
        ple_inv_bal_one_temp.write({'line_final_ids': [(6, 0, ple_inv_final_balances.ids)]})
        ple_inv_initial_balances.write({'ple_report_inv_val_one_id': ple_inv_bal_one_temp.id})
        ple_inv_final_balances.write({'ple_report_inv_val_one_id': ple_inv_bal_one_temp.id})

        self.assertRaises(AccessError, ple_inv_bal_one_temp.action_compute_initial_balance_302())
        self.assertRaises(AccessError, ple_inv_bal_one_temp.capture_initial_balances_id())
        print("---------------------------------TEST2------------------------------------------------")
    
    def test_ple_inv_bal_07_methods(self):   

        ple_inv_bal_one_temp = self.create_ple_inv_bal_one()
        inv_bal_line_temp = self.create_ple_inv_bal_line_one()

        ple_inv_bal_one_temp.write({'line_ids': [(6, 0, inv_bal_line_temp.ids)]})
        inv_bal_line_temp.write({'ple_report_inv_val_one_id': ple_inv_bal_one_temp.id})

        ple_inv_initial_balances = self.create_initial_balances()
        ple_inv_final_balances = self.create_final_balances()

        ple_inv_bal_one_temp.write({'line_initial_ids': [(6, 0, ple_inv_initial_balances.ids)]})
        ple_inv_bal_one_temp.write({'line_final_ids': [(6, 0, ple_inv_final_balances.ids)]})
        ple_inv_initial_balances.write({'ple_report_inv_val_one_id': ple_inv_bal_one_temp.id})
        ple_inv_final_balances.write({'ple_report_inv_val_one_id': ple_inv_bal_one_temp.id})

        
        ple_inv_bal_one_temp.create_book_07()

        
        self.assertIsNotNone(ple_inv_bal_one_temp.m2o_ple_report_inv_bal_07)
        self.assertIsNotNone(ple_inv_bal_one_temp.xls_filename_07)
        self.assertIsNotNone(ple_inv_bal_one_temp.xls_binary_07)
        self.assertIsNotNone(ple_inv_bal_one_temp.txt_filename_07)
        self.assertIsNotNone(ple_inv_bal_one_temp.txt_binary_07)
        self.assertIsNotNone(ple_inv_bal_one_temp.pdf_filename_07)
        self.assertIsNotNone(ple_inv_bal_one_temp.pdf_binary_07)        

       
        ple_inv_bal_one_temp.action_generate_excel()
        print("----------------------------------TEST3-----------------------------------")
      