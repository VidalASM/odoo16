from odoo import fields, models, api


class PleInvBal1One(models.Model):
    _inherit = 'ple.report.inv.bal.one'

    xls_filename_04 = fields.Char(string='Filaname_04 .xls')
    xls_binary_04 = fields.Binary(string='Reporte .XLS 3.4')
    txt_filename_04 = fields.Char(string='Filaname_04 .txt')
    txt_binary_04 = fields.Binary(string='Reporte .TXT 3.4')
    pdf_filename_04 = fields.Char(string='Filaname_04 .pdf')
    pdf_binary_04 = fields.Binary(string='Reporte .PDF 3.4')

    m2o_ple_report_inv_bal_04 = fields.Many2one('ple.report.inv.bal.04')

    def create_book_04(self):
        self.m2o_ple_report_inv_bal_04 = self.env[
            "ple.report.inv.bal.04"].create(
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

        self.m2o_ple_report_inv_bal_04.action_generate_excel()

        self.xls_filename_04 = self.m2o_ple_report_inv_bal_04.xls_filename
        self.xls_binary_04 = self.m2o_ple_report_inv_bal_04.xls_binary
        self.txt_filename_04 = self.m2o_ple_report_inv_bal_04.txt_filename
        self.txt_binary_04 = self.m2o_ple_report_inv_bal_04.txt_binary
        self.pdf_filename_04 = self.m2o_ple_report_inv_bal_04.pdf_filename
        self.pdf_binary_04 = self.m2o_ple_report_inv_bal_04.pdf_binary

        self.m2o_ple_report_inv_bal_04.unlink();

    def action_generate_excel(self):
        self.create_book_04()
        super(PleInvBal1One, self).action_generate_excel()
