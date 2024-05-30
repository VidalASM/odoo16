from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime,timedelta

class TestReportAccount(TransactionCase):
        
    def setUp(self):
        super(TestReportAccount, self).setUp()
    
        self.ts_account = self.env['account.account'].create({
            'name':'ExampleAccount',
            'code':'8530001',
            'deprecated':False,
            'account_type':'asset_current',
            'include_initial_balance':True
        })
        
        print("-----SETUP OK----")
        
    def test_field_report_account(self):
        self.assertEqual(self.ts_account.name,'ExampleAccount')
        self.assertEqual(self.ts_account.code,'8530001')
        self.assertFalse(self.ts_account.deprecated)    
        self.assertEqual(self.ts_account.account_type,'asset_current')
        self.assertTrue(self.ts_account.include_initial_balance)
                    
        print("----TEST FIELD REPORT OK----")