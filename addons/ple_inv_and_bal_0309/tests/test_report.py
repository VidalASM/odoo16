from odoo.tests.common import TransactionCase
from datetime import date


class TestGetLines(TransactionCase):
    def setUp(self):
        super(TestGetLines, self).setUp()

        self.get_lines_model = self.env['report.ple_inv_and_bal_0309.print_status_finance']
        self.ple_model = self.env['ple.report.inv.bal.09']
        self.date_start = date.today().replace(month=1, day=1)
        self.date_end = date.today()
        self.company = self.env.ref('base.main_company')

    def test_get_report_values(self):

        ple_report1 = self.ple_model.create({
            'date_start': self.date_start,
            'date_end': self.date_end,
            'company_id': self.company.id,
            'state_send': '0',
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
        })

        ple_report2 = self.ple_model.create({
            'date_start': self.date_start,
            'date_end': self.date_end,
            'company_id': self.company.id,
            'state_send': '0',
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
        })

        result = self.get_lines_model._get_report_values(
            docids=[ple_report1.id, ple_report2.id], data={})

        self.assertTrue(result)
        self.assertIn('doc_ids', result)
        self.assertIn('docs', result)
        self.assertIn('data', result)

        self.assertEqual(result['doc_ids'], [ple_report1.id, ple_report2.id])

        self.assertTrue(result['docs'])
        self.assertIn(ple_report1, result['docs'])
        self.assertIn(ple_report2, result['docs'])

        self.assertEqual(result['data'], {})
