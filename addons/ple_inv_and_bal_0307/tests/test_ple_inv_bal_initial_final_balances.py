from odoo.tests.common import TransactionCase
from datetime import datetime,date


class TestPleInvBalLinesFinal07(TransactionCase):

    def setUp(self):
        super(TestPleInvBalLinesFinal07, self).setUp()      
        self.company_temp = self.env['res.company'].create({
            'name': 'Company test',
        }) 
        self.report = self.env['ple.report.inv.bal.07'].create({           
            'financial_statements_catalog': '01',
            'eeff_presentation_opportunity': '01',
            'company_id': self.company_temp.id,
            'date_start': date(2023, 7, 11),
            'date_end': date(2023, 1, 15),
            'state': 'draft',
            'state_send': '0',
            'txt_filename' :'Filaname .txt',
            'txt_binary' : 'Reporte .TXT 3.7',
            'pdf_filename': 'Reporte .PDF 3.7',
            'pdf_binary' : 'Reporte .PDF 3.7',               
        })       
    def test_ple_inv_bal_lines_final_07(self):            
        initial_line = self.env['ple.inv.bal.line.initial.balances.07'].create({
            'ple_report_inv_val_id': self.report.id,
            'period': '202307',
            'stock_catalog': 'CAT001',
            'stock_type': 'Type001',
            'default_code': 'CODE001',
            'code_catalog_used': 'CAT_USED001',
            'unspsc_code_id': 12345,
            'product_id': 'PRODUCT001',
            'product_description': 'Test Product',
            'product_udm': 'UOM001',
            'quantity_product_hand': 100,
            'standard_price': 10.50,
            'property_cost_method': 'average',
            'aml_id': 9876,
            'total': 1050,
            'company_id': 1,
            'last_date': '2023-07-30',
        })     
        final_line = self.env['ple.inv.bal.line.final.balances.07'].create({
            'ple_report_inv_val_id': self.report.id,
            'period': '202307',
            'stock_catalog': 'CAT001',
            'stock_type': 'Type001',
            'default_code': 'CODE001',
            'code_catalog_used': 'CAT_USED001',
            'unspsc_code_id': 12345,
            'product_id': 'PRODUCT001',
            'product_description': 'Test Product',
            'product_udm': 'UOM001',
            'quantity_product_hand': 100,
            'standard_price': 10.50,
            'property_cost_method': 'average',
            'aml_id': 9876,
            'total': 1050,
            'company_id': 1,
            'last_date': '2023-07-18',
        })    
        self.report.action_generate_initial_whit_ending_balances_07()     
 
        self.assertTrue(final_line.id, "The final line should be created successfully.")
        self.assertEqual(final_line.ple_report_inv_val_id, self.report, "Report ID should match.")
        
        self.assertEqual(self.report.line_final_ids, final_line, "The final line should be stored in the report.")
    
        self.assertEqual(final_line.period, '202307', "Period field should match.")
        self.assertEqual(final_line.stock_catalog, 'CAT001', "Stock Catalog field should match.")
        self.assertEqual(final_line.stock_type, 'Type001', "Stock Type field should match.")
        self.assertEqual(final_line.default_code, 'CODE001', "Default Code field should match.")
        self.assertEqual(final_line.code_catalog_used, 'CAT_USED001', "Code Catalog Used field should match.")
        self.assertEqual(final_line.unspsc_code_id, 12345, "UNSPSC Code ID field should match.")
        self.assertEqual(final_line.product_id, 'PRODUCT001', "Product ID field should match.")
        self.assertEqual(final_line.product_description, 'Test Product', "Product Description field should match.")
        self.assertEqual(final_line.product_udm, 'UOM001', "Product UDM field should match.")
        self.assertAlmostEqual(final_line.quantity_product_hand, 100, delta=0.0001, msg="Quantity Product Hand field should match.")
        self.assertAlmostEqual(final_line.standard_price, 10.50, delta=0.0001, msg="Standard Price field should match.")
        self.assertEqual(final_line.property_cost_method, 'average', "Property Cost Method field should match.")
        self.assertEqual(final_line.aml_id, 9876, "AML ID field should match.")
        self.assertAlmostEqual(final_line.total, 1050, delta=0.0001, msg="Total field should match.")
        self.assertEqual(final_line.company_id, 1, "Company ID field should match.")
        self.assertEqual(final_line.last_date, datetime.strptime('2023-07-18', '%Y-%m-%d').date(), "Last Date field should match.")    
 
        self.assertTrue(initial_line.id, "The initial line should be created successfully.")
        self.assertEqual(initial_line.ple_report_inv_val_id, self.report, "Report ID should match.")
      
        self.assertEqual(self.report.line_initial_ids, initial_line, "The initial line should be stored in the report.")
     
        self.assertEqual(initial_line.period, '202307', "Period field should match.")
        self.assertEqual(initial_line.stock_catalog, 'CAT001', "Stock Catalog field should match.")
        self.assertEqual(initial_line.stock_type, 'Type001', "Stock Type field should match.")
        self.assertEqual(initial_line.default_code, 'CODE001', "Default Code field should match.")
        self.assertEqual(initial_line.code_catalog_used, 'CAT_USED001', "Code Catalog Used field should match.")
        self.assertEqual(initial_line.unspsc_code_id, 12345, "UNSPSC Code ID field should match.")
        self.assertEqual(initial_line.product_id, 'PRODUCT001', "Product ID field should match.")
        self.assertEqual(initial_line.product_description, 'Test Product', "Product Description field should match.")
        self.assertEqual(initial_line.product_udm, 'UOM001', "Product UDM field should match.")
        self.assertAlmostEqual(initial_line.quantity_product_hand, 100, delta=0.0001, msg="Quantity Product Hand field should match.")
        self.assertAlmostEqual(initial_line.standard_price, 10.50, delta=0.0001, msg="Standard Price field should match.")
        self.assertEqual(initial_line.property_cost_method, 'average', "Property Cost Method field should match.")
        self.assertEqual(initial_line.aml_id, 9876, "AML ID field should match.")
        self.assertAlmostEqual(initial_line.total, 1050, delta=0.0001, msg="Total field should match.")
        self.assertEqual(initial_line.company_id, 1, "Company ID field should match.")
        self.assertEqual(initial_line.last_date, datetime.strptime('2023-07-30', '%Y-%m-%d').date(), "Last Date field should match.")
        
        
        print("----------------BALANCE TEST SUCCESSFULLY---------------------")
