from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime,timedelta

class TestPleInVal(TransactionCase):
        
    def setUp(self):
        super(TestPleInVal, self).setUp()
        
        self.date_start = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        self.date_end = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        self.date_ple = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        self.ple_0324 = self.env['ple.report.inv.bal.24'].create({
            'financial_statements_catalog': '01',
            'state_send':'0',
            'eeff_presentation_opportunity':'02',
            'date_start':self.date_start,
            'date_end':self.date_end,
            'state':'draft',
            'date_ple':self.date_ple
        })     
        
        self.ple_line_0324 = self.env['ple.report.inv.bal.line.24'].create({
            'name': 'NameReportExample',
            'sequence':10,
            'catalog_code':'report001',
            'financial_state_code':'reportExample',
            'credit':'100.00',
            'state':'draft'
        })
        
        print("----SET UP OK---")
                
    def test_field_ple_in_val(self):
        self.assertEqual(self.ple_0324.financial_statements_catalog,'01')
        self.assertEqual(self.ple_0324.state_send,'0')
        self.assertEqual(self.ple_0324.eeff_presentation_opportunity,'02')
        self.assertEqual(self.ple_0324.date_start, datetime.strptime(self.date_start, "%Y-%m-%d").date())
        self.assertEqual(self.ple_0324.date_end, datetime.strptime(self.date_end, "%Y-%m-%d").date())
        self.assertEqual(self.ple_0324.state, 'draft')
        self.assertEqual(self.ple_0324.date_ple, datetime.strptime(self.date_ple, "%Y-%m-%d").date())
        
        print("----TEST FIELDS PLE OK----")
        
    def test_field_ple_in_val_line(self):
        self.assertEqual(self.ple_line_0324.name,'NameReportExample')
        self.assertEqual(self.ple_line_0324.sequence,10)
        self.assertEqual(self.ple_line_0324.catalog_code,'report001')
        self.assertEqual(self.ple_line_0324.financial_state_code,'reportExample')
        self.assertEqual(self.ple_line_0324.credit,'100.00')
        self.assertEqual(self.ple_line_0324.state,'draft')
        
        print("----TEST FIELDS PLE LINE OK----")
    
    def test_function_ple_in_val(self):
        self.assertTrue(self.ple_0324.action_generate_report())
        self.assertIsNone(self.ple_0324.action_close())
        self.assertIsNone(self.ple_0324.action_rollback())
        self.assertIsNone(self.ple_0324.action_generate_excel())

        print("----TEST FUNCTION PLE OK----")

        