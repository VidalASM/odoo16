from odoo.tests.common import TransactionCase

class TestPleInvBal03(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestPleInvBal03, self).setUp(*args, **kwargs)
        self.report_model = self.env['ple.report.inv.bal.03']
        self.ple_report = self.report_model.create({
            'date_start': '2023-07-01',
            'date_end': '2023-12-31',
            'financial_statements_catalog': '07',
            'eeff_presentation_opportunity': '01',
            'state_send': '1' 
        })
    
    def test_action_generate_report(self):
        self.ple_report.action_generate_report()
        
        self.assertTrue(self.ple_report.exists())

        print("============ TEST 1 ==============")

    def test_action_generate_excel(self):
        self.ple_report.action_generate_excel()
        
        self.assertTrue(self.ple_report.xls_filename)
        self.assertTrue(self.ple_report.xls_binary)

        print("============ TEST 2 ==============")