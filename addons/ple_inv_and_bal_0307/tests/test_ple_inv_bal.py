from odoo.tests import common
from datetime import date

class TestPleInvBalLines(common.TransactionCase):

    def setUp(self):
        super(TestPleInvBalLines, self).setUp()
        self.ple_inv_bal_lines_model = self.env['ple.report.inv.bal.line.07']
        self.ple_report_inv_val_07_model = self.env['ple.report.inv.bal.07']
        
        self.company_temp = self.env['res.company'].create({
            'name': 'Company test',
        })
        
    def create_ple_inv_bal_lines(self):       
        common_obj = {
            'period': 'Periodo prueba',
            'stock_catalog': 'Código de catálogo prueba',
            'stock_type': 'Tipo de Existencia prueba',
            'default_code': 'Código propio de la existencia prueba',
            'code_catalog_used': 'codigo catalogo utilizado prueba',
            'unspsc_code_id': 12345,
            'product_id': 'Product_id prueba',
            'product_description': 'Descripcion de existencia prueba',
            'product_udm': 'product udm prueba',
            'quantity_product_hand': 10.0,
            'standard_price': 100.0,
            'property_cost_method': 'Property cost method prueba',
            'aml_id': 6789,
            'total': 1000.0,
            'company_id': 1,
            'last_date': date.today(),
        }
        
        return self.ple_inv_bal_lines_model.create(common_obj)
        

    def create_ple_report_inv_val_07(self):      
        return self.ple_report_inv_val_07_model.create(
             {
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
            }       
        )       

    def test_ple_inv_bal_lines(self):       
        ple_report_inv_val_07 = self.create_ple_report_inv_val_07()
        ple_inv_bal_lines = self.create_ple_inv_bal_lines()
        ple_inv_bal_lines.ple_report_inv_val_07_id = ple_report_inv_val_07 
        self.assertTrue(ple_inv_bal_lines)
        self.assertEqual(ple_inv_bal_lines.ple_report_inv_val_07_id, ple_report_inv_val_07)        
        ple_inv_bal_lines_read = self.ple_inv_bal_lines_model.browse(ple_inv_bal_lines.id)
        self.assertEqual(ple_inv_bal_lines_read.period, 'Periodo prueba')
        self.assertEqual(ple_inv_bal_lines_read.stock_catalog, 'Código de catálogo prueba')
        self.assertEqual(ple_inv_bal_lines_read.stock_type, 'Tipo de Existencia prueba')     
        ple_inv_bal_lines.write({'period': 'Nuevo periodo'})
        self.assertEqual(ple_inv_bal_lines.period, 'Nuevo periodo')        
        ple_inv_bal_lines.unlink()
        self.assertFalse(self.ple_inv_bal_lines_model.search([('id', '=', ple_inv_bal_lines.id)]))       
        ple_report_inv_val_07.action_generate_report()    
        ple_report_inv_val_07.action_generate_excel()
        print("-------------------------------FINAL TEST COMPLETE-------------------------------")

