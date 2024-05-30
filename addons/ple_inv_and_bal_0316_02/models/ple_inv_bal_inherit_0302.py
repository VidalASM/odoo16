from odoo import fields, models, api


class PleInvBal1One(models.Model):
    _inherit = 'ple.report.inv.bal.one'

    xls_filename_16_02 = fields.Char(string='Filaname_16_02 .xls')
    xls_binary_16_02 = fields.Binary(string='Reporte .XLS 3.16.2')
    txt_filename_16_02 = fields.Char(string='Filaname_16_02 .txt')
    txt_binary_16_02 = fields.Binary(string='Reporte .TXT 3.16.2')

    m2o_ple_report_inv_bal_16_02 = fields.Many2one('ple.report.inv.bal.16.2')

    def create_book_16_02(self):

        self.m2o_ple_report_inv_bal_16_02 = self.env["ple.report.inv.bal.16.2"].create(
            {
                'company_id': self.company_id.id,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'state_send': self.state_send,
                'date_ple': self.date_ple,
                'financial_statements_catalog': self.financial_statements_catalog,
                'eeff_presentation_opportunity': self.eeff_presentation_opportunity,
            }
        )

        self.m2o_ple_report_inv_bal_16_02.action_generate_excel()

        self.xls_filename_16_02 = self.m2o_ple_report_inv_bal_16_02.xls_filename
        self.xls_binary_16_02 = self.m2o_ple_report_inv_bal_16_02.xls_binary
        self.txt_filename_16_02 = self.m2o_ple_report_inv_bal_16_02.txt_filename
        self.txt_binary_16_02 = self.m2o_ple_report_inv_bal_16_02.txt_binary

        self.m2o_ple_report_inv_bal_16_02.unlink();

    def action_generate_excel(self):
        self.create_book_16_02()
        super(PleInvBal1One, self).action_generate_excel()
