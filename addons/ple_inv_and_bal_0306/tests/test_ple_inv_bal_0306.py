from odoo.tests import common

class TestPleReportInvBal06(common.TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestPleReportInvBal06, self).setUp(*args, **kwargs)
        self.report_model = self.env['ple.report.inv.bal.06']
        self.ple_report = self.report_model.create({
            'date_start': '2023-01-01',
            'date_end': '2023-12-31',
            'company_id': self.env.ref('base.main_company').id,
            'financial_statements_catalog': '07',
            'eeff_presentation_opportunity': '01',
            'state': 'draft',
            'state_send': '1'
        })

    def test_generate_report(self):
        self.ple_report.action_generate_report()

        self.assertTrue(self.ple_report.exists())
        print("=======================   TEST 1 =======================")
        
    def test_generate_excel(self):
        self.ple_report.action_generate_excel()

        self.assertTrue(self.ple_report.xls_filename)
        self.assertTrue(self.ple_report.xls_binary)        
        print("=======================   TEST 2 =======================")

    def tearDown(self):
        super(TestPleReportInvBal06, self).tearDown()
