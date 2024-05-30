from odoo import fields, models, api


class PleInvBal1One(models.Model):
    _inherit = 'ple.report.inv.bal.one'

    xls_filename_05 = fields.Char(string='Filaname_05 .xls')
    xls_binary_05 = fields.Binary(string='Reporte .XLS 3.5')
    txt_filename_05 = fields.Char(string='Filaname_05 .txt')
    txt_binary_05 = fields.Binary(string='Reporte .TXT 3.5')
    pdf_filename_05 = fields.Char(string='Filaname_05 .pdf')
    pdf_binary_05 = fields.Binary(string='Reporte .PDF 3.5')

    m2o_ple_report_inv_bal_05 = fields.Many2one('ple.report.inv.bal.05')

    def create_book_05(self):

        self.m2o_ple_report_inv_bal_05 = self.env["ple.report.inv.bal.05"].create(
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

        self.m2o_ple_report_inv_bal_05.action_generate_excel()

        self.xls_filename_05 = self.m2o_ple_report_inv_bal_05.xls_filename
        self.xls_binary_05 = self.m2o_ple_report_inv_bal_05.xls_binary
        self.txt_filename_05 = self.m2o_ple_report_inv_bal_05.txt_filename
        self.txt_binary_05 = self.m2o_ple_report_inv_bal_05.txt_binary
        self.pdf_filename_05 = self.m2o_ple_report_inv_bal_05.pdf_filename
        self.pdf_binary_05 = self.m2o_ple_report_inv_bal_05.pdf_binary

        self.m2o_ple_report_inv_bal_05.unlink();

    def action_generate_excel(self):
        self.create_book_05()
        super(PleInvBal1One, self).action_generate_excel()
