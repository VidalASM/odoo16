from odoo import fields, models, api


class PleInvBal1One(models.Model):
    _inherit = 'ple.report.inv.bal.one'

    xls_filename_03 = fields.Char(string='Filaname_03 .xls')
    xls_binary_03 = fields.Binary(string='Reporte .XLS 3.3')
    txt_filename_03 = fields.Char(string='Filaname_03 .txt')
    txt_binary_03 = fields.Binary(string='Reporte .TXT 3.3')
    pdf_filename_03 = fields.Char(string='Filaname_03 .pdf')
    pdf_binary_03 = fields.Binary(string='Reporte .PDF 3.3')

    m2o_ple_report_inv_bal_03 = fields.Many2one('ple.report.inv.bal.03')

    def create_book_03(self):
        self.m2o_ple_report_inv_bal_03 = self.env[
            "ple.report.inv.bal.03"].create(
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

        self.m2o_ple_report_inv_bal_03.action_generate_excel()

        self.xls_filename_03 = self.m2o_ple_report_inv_bal_03.xls_filename
        self.xls_binary_03 = self.m2o_ple_report_inv_bal_03.xls_binary
        self.txt_filename_03 = self.m2o_ple_report_inv_bal_03.txt_filename
        self.txt_binary_03 = self.m2o_ple_report_inv_bal_03.txt_binary
        self.pdf_filename_03 = self.m2o_ple_report_inv_bal_03.pdf_filename
        self.pdf_binary_03 = self.m2o_ple_report_inv_bal_03.pdf_binary

        self.m2o_ple_report_inv_bal_03.unlink();

    def action_generate_excel(self):
        self.create_book_03()
        super(PleInvBal1One, self).action_generate_excel()
