from odoo.tests.common import TransactionCase

class TestPleInvBal(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestPleInvBal, self).setUp(*args, **kwargs)
        self.report_model = self.env['ple.report.inv.bal.20']
        self.ple_report = self.report_model.create({
            'date_start': '2023-02-02',
            'date_end': '2023-08-31',
            'financial_statements_catalog': '09',
            'eeff_presentation_opportunity': '01',
            'state_send': '1' 
        })

    def test_action_generate_report(self):
        self.ple_report.action_generate_report()
        
        self.assertTrue(self.ple_report.exists())

    def test_action_generate_excel(self):
        self.ple_report.action_generate_excel()
        
        self.assertTrue(self.ple_report.xls_filename)
        self.assertTrue(self.ple_report.xls_binary)
        
        
    def test_action_generate_pdf(self):
        self.ple_report.action_generate_excel()
        self.assertTrue(self.ple_report.pdf_filename)
        self.assertTrue(self.ple_report.pdf_binary)

    def test_name_get(self):
        name = self.ple_report.name_get()[0][1]
        expected_name = "02/02/2023 - 31/08/2023"
        self.assertEqual(name, expected_name)
