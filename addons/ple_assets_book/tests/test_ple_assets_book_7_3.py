from pytz import timezone
from datetime import datetime
import unittest

from odoo.tests.common import tagged
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged('post_install', '-at_install')
class TestAssetsReport0703(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.frozen_today = datetime(year=2023, month=1, day=1, hour=0, minute=0, second=0, tzinfo=timezone('utc'))

        cls.company_data['company'].write({
            'vat': "20557912879",
            'country_id': cls.env.ref('base.pe').id,
            'ple_type_contributor': 'CUO',
        })

    def setUp(self):
        super(TestAssetsReport0703, self).setUp()
        self.obj = self.env['ple.report.assets.book']
        self.obj.date_start = datetime.strptime('2023-01-01', '%Y-%m-%d').date()
        self.obj.date_end = datetime.strptime('2023-01-31', '%Y-%m-%d').date()
        self.obj.company_id = self.ref("base.main_company")
        self.data = [
            {
                'period': '20220101',
                'cuo': '00001',
                'correlative': '001',
                'asset_catalog_code': 'CAT001',
                'asset_code': 'ASSET001',
                'acquisition_date': '01/01/2022',
                'value_acquisition_exchange': 100.0,
                'foreign_currency_exchange_rate': 1.0,
                'value_acquisition_local': 100.0,
                'currency_exchange_rate_3112': 1.0,
                'adjust_difference_exchange_rate': 0.0,
                'amount_withdrawals': 10.0,
                'dep_amount_withdrawals': 5.0,
                'amount_other_ple': 15.0
            }
        ]

    def test_get_content_excel(self):
        content = self.report.get_content_excel()
        self.assertGreater(len(content.getvalue()), 0)
        print('------------TEST_1 OK------------')

    def test_get_filename(self):
        filename_xlsx = self.report.get_filename(file_type='xlsx', book_identifier='070300')
        filename_txt = self.report.get_filename(file_type='txt', book_identifier='070300')
        self.assertEqual(filename_xlsx, 'LE2055791287920220100011100.xlsx')
        self.assertEqual(filename_txt, 'LE2055791287920220100011100.txt')
        print('------------TEST_2 OK------------')
