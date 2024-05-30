

from datetime import date
from io import BytesIO
import re
from odoo.tests.common import TransactionCase
from odoo.tools.misc import xlsxwriter
from ..reports.report_inv_bal_09 import ReportInvBalNineExcel, ReportInvBalNineTxt
from datetime import datetime


class TestReportInvBalNineExcel(TransactionCase):

    def test_get_filename(self):
        obj = self.env['ple.report.inv.bal.09'].create({
            'company_id': self.env.company.id,
            'date_start': date(2023, 7, 1),
            'date_end': date(2023, 7, 31),
            'state_send': '0',
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
        })

        report_excel = ReportInvBalNineExcel(obj, [])
        filename = report_excel.get_filename()

        self.assertEqual(filename, 'Libro_Activos Intangibles_202307.xlsx')


class TestReportInvBalNineTxt(TransactionCase):
    def test_get_content(self):
        data_1 = [
            {
                'date': '2023-07-19', 'name_s': 'Asiento de Prueba 1', 'ple_correlative': '001',
                'operation_date': datetime.strptime('2023-07-18', '%Y-%m-%d'), 'code_account': 'Código1',
                'name_aml': 'Descripción1', 'balance': 100, 'balance_amortization_xls': 50, 'state': 'Activo'
            },
            {
                'date': '2023-07-20', 'name_s': 'Asiento de Prueba 2', 'ple_correlative': '002',
                'operation_date': datetime.strptime('2023-07-19', '%Y-%m-%d'), 'code_account': 'Código2',
                'name_aml': 'Descripción2', 'balance': 200, 'balance_amortization_xls': 75, 'state': 'Inactivo'
            }
        ]

        obj = self.env['ple.report.inv.bal.09'].create({
            'company_id': self.env.company.id,
            'date_start': date(2023, 7, 1),
            'date_end': date(2023, 7, 31),
            'state_send': '0',
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
        })

        report_txt = ReportInvBalNineTxt(obj, data_1)
        content = report_txt.get_content()

        expected_content = (
            '2023-07-19|AsientodePrueba1|001|18/07/2023|Cdigo1|Descripción1|100.00|50.00|Activo|\r\n'
            '2023-07-20|AsientodePrueba2|002|19/07/2023|Cdigo2|Descripción2|200.00|75.00|Inactivo|\r\n'
        )
        self.assertEqual(content, expected_content)

    def test_get_filename(self):
        obj = self.env['ple.report.inv.bal.09'].create({
            'company_id': self.env.company.id,
            'date_start': date(2023, 7, 1),
            'date_end': date(2023, 7, 31),
            'state_send': '0',
            'eeff_presentation_opportunity': '01',
            'financial_statements_catalog': '02',
        })

        report_txt = ReportInvBalNineTxt(obj, [])
        filename = report_txt.get_filename()

        self.assertEqual(filename, 'LE2055158304120230731030900010011.txt')
