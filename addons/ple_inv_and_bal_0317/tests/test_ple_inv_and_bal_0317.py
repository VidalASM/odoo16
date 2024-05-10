from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, ValidationError
from datetime import date

@tagged('-at_install', 'post_install')
class TestPleInvAndBal0317(TransactionCase):

    @classmethod
    def setUpClass(self):
        super(TestPleInvAndBal0317, self).setUpClass()
        self.ple_report_inv_bal_0317 = self.env['ple.report.inv.bal.seventeen']

        self.ple_initial_balances_seveenten = self.env['ple.initial.balances.seveenten']
        self.ple_transfers_cancellations_seveenten = self.env['ple.transfers.cancellations']
        self.ple_additions_deductions_seveenten = self.env['ple.addition.deduction']

        self.trial_balances_catalog = self.env['trial.balances.catalog']

        self.company_temp = self.env['res.company'].create({
            'name': 'Company test',
        })

        self.account_account = self.env['account.account']
        self.account_journal = self.env['account.journal']


    def create_ple_inv_bal_17(self):
        temp_ple_inv_bal_17 = self.ple_report_inv_bal_0317.create({
            'company_id': self.company_temp.id,
            'date_start': date(2023, 7, 11),
            'date_end': date(2023, 8, 15),
            'state': 'draft',
            'state_send': '0',
            'date_ple': date(2023, 8, 15),
            'financial_statements_catalog': '01',
            'eeff_presentation_opportunity': '01',
            # 'line_initial_balances_ids':'',
            # 'line_transfers_cancellations_ids':'',
            # 'line_additions_deductions_ids':'',
        })
        return temp_ple_inv_bal_17

    def create_initial_balances_seveenten(self):
        temp_ple_initial_balances_seveenten = self.ple_initial_balances_seveenten.create({
            # 'ple_report_inv_val_seventeen_id': 'ple.report.inv.bal.seventeen',
            # 'trial_balances_catalog_id': '',trial.balances.catalog
            'name': 'initial balances test',
            'debit': '1500.0',
            'credit': '1500.0',
            'sequence': 1,
        })
        return temp_ple_initial_balances_seveenten

    def create_transfer_cancellations(self):
        temp_transfer_cancellations = self.ple_transfers_cancellations_seveenten.create({
            # ple_report_inv_val_seventeen_id
            # trial_balances_catalog_id
            'transfers_cancellations_selection': 'transfers',
            'amount': '1500.0',
        })
        return temp_transfer_cancellations

    def create_adittions_deductions(self):
        temp_adittions_deductions = self.ple_additions_deductions_seveenten.create({
            # ple_report_inv_val_seventeen_id
            # trial_balances_catalog_id
            'transfers_additions_selection': 'additions',
            'amount': '1500.0'
        })
        return temp_adittions_deductions


    def create_trial_balances(self):
        temp_trial_balances = self.trial_balances_catalog.create({
            'code':'code test',
            'name':'name test',
            'sequence':1,
        })
        return temp_trial_balances


    def test_ple_report_inv_bal_17(self):
        ple_inv_bal_17_temp = self.create_ple_inv_bal_17()
        initial_balances_seveenten_temp = self.create_initial_balances_seveenten()
        transfer_cancellations_temp = self.create_transfer_cancellations()
        adittions_deductions_temp = self.create_adittions_deductions()
        trial_balances_temp = self.create_trial_balances()

        initial_balances_seveenten_temp.write({'trial_balances_catalog_id': trial_balances_temp.id})
        transfer_cancellations_temp.write({'trial_balances_catalog_id': trial_balances_temp.id})
        adittions_deductions_temp.write({'trial_balances_catalog_id': trial_balances_temp.id})

        ple_inv_bal_17_temp.write({'line_initial_balances_ids': [(6, 0, initial_balances_seveenten_temp.ids)]})
        ple_inv_bal_17_temp.write({'line_transfers_cancellations_ids': [(6, 0, transfer_cancellations_temp.ids)]})
        ple_inv_bal_17_temp.write({'line_additions_deductions_ids': [(6, 0, adittions_deductions_temp.ids)]})
        initial_balances_seveenten_temp.write({'ple_report_inv_val_seventeen_id': ple_inv_bal_17_temp.id})
        transfer_cancellations_temp.write({'ple_report_inv_val_seventeen_id': ple_inv_bal_17_temp.id})
        adittions_deductions_temp.write({'ple_report_inv_val_seventeen_id': ple_inv_bal_17_temp.id})

        self.assertRaises(ValidationError, ple_inv_bal_17_temp.action_generate_data_seventeen())
        self.assertIsNone(ple_inv_bal_17_temp.action_generate_data_seventeen())

        print("----------------------------------TEST 0317 Parte 1 ----------------------------------")

        year_month = ple_inv_bal_17_temp.date_end.strftime('%Y%m')
        self.assertEqual(ple_inv_bal_17_temp.xls_filename, f'Libro_Balance_Comprobación_{year_month}.xlsx')
        year, month, day = ple_inv_bal_17_temp.date_end.strftime('%Y/%m/%d').split('/')
        self.assertEqual(ple_inv_bal_17_temp.pdf_filename, f'Libro_Balance_Comprobación_{year}{month}.pdf')
        print("----------------------------------TEST 0317 Parte 2 ----------------------------------")