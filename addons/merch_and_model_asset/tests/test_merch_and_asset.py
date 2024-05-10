from pytz import timezone
from datetime import datetime

from odoo.tests.common import tagged
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged('post_install', '-at_install')
class TestAssets(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref)
        cls.car = cls.create_asset(value=60000, periodicity="yearly", periods=5, method="linear", salvage_value=0)

    @classmethod
    def create_asset(cls, value, periodicity, periods, degressive_factor=None, import_depreciation=0, **kwargs):
        if degressive_factor is not None:
            kwargs["method_progress_factor"] = degressive_factor
        return cls.env['account.asset'].create({
            'name': 'nice asset',
            'account_asset_id': cls.company_data['default_account_assets'].id,
            'account_depreciation_id': cls.company_data['default_account_assets'].copy().id,
            'account_depreciation_expense_id': cls.company_data['default_account_expense'].id,
            'journal_id': cls.company_data['default_journal_misc'].id,
            'asset_type': "purchase",
            'acquisition_date': "2020-02-01",
            'prorata_computation_type': 'none',
            'original_value': value,
            'salvage_value': 0,
            'method_number': periods,
            'method_period': '12' if periodicity == "yearly" else '1',
            'method': "linear",
            'asset_brand': 'Marca prueba',
            'asset_model': 'Modelo Prueba',
            'asset_series': 'serie de prueba',
            'already_depreciated_amount_import': import_depreciation,
            **kwargs,
        })

    @classmethod
    def _get_depreciation_move_values(cls, date, depreciation_value, remaining_value, depreciated_value, state):
        print('MERCH AND ASSET OK -----------------------------')
        return {
            'date': fields.Date.from_string(date),
            'depreciation_value': depreciation_value,
            'asset_remaining_value': remaining_value,
            'asset_depreciated_value': depreciated_value,
            'state': state,
        }

    def test_linear_purchase_5_years_no_prorata_asset(self):
        self.car.validate()

        self.assertEqual(self.car.state, 'open')
        self.assertEqual(self.car.book_value, 36000)
        self.assertRecordValues(self.car.depreciation_move_ids, [
            self._get_depreciation_move_values(date='2020-12-31', depreciation_value=12000, remaining_value=48000, depreciated_value=12000, state='posted'),
            self._get_depreciation_move_values(date='2021-12-31', depreciation_value=12000, remaining_value=36000, depreciated_value=24000, state='posted'),
            self._get_depreciation_move_values(date='2022-12-31', depreciation_value=12000, remaining_value=24000, depreciated_value=36000, state='draft'),
            self._get_depreciation_move_values(date='2023-12-31', depreciation_value=12000, remaining_value=12000, depreciated_value=48000, state='draft'),
            self._get_depreciation_move_values(date='2024-12-31', depreciation_value=12000, remaining_value=0, depreciated_value=60000, state='draft'),
        ])
        print('MERCH AND ASSET OK -----------------------------')