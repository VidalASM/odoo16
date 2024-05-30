from odoo.tests import common
from datetime import date
class TestCompany(common.TransactionCase):
    def setUp(self):
        super().setUp()     
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})
        self.company = self.env['res.company'].create({'name': 'Test Company'})
        print("---------------------- OK1----------------------------")
    def test_lines_report_0316(self):    
        # Crea un registro de report.ple.031601.fields
        report_fields = self.env['report.ple.031601.fields'].create({
            'company_id': self.company.id,
            'social_reason': self.partner.id,
            'partition_type_code': '01',
            'participations_number': '12345',
            'participations_percentage': 50.0,
            'is_member': True,
            'date_incorporation_partner': '2023-01-01',
        })             
        self.assertEqual(report_fields.company_id, self.company)
        self.assertEqual(report_fields.social_reason, self.partner)
        self.assertEqual(report_fields.partition_type_code, '01')
        self.assertEqual(report_fields.participations_number, '12345')
        self.assertEqual(report_fields.participations_percentage, 50.0)
        self.assertTrue(report_fields.is_member)
        self.assertEqual(report_fields.date_incorporation_partner, date(2023, 1, 1))
        print("---------------------- OK----------------------------")
    