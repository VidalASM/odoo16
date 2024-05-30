from odoo import fields, models, api
from ..reports.report_inv_bal_09 import ReportInvBalNineExcel, ReportInvBalNineTxt

import base64
from odoo.exceptions import ValidationError
from itertools import groupby


class PleInvBal09(models.Model):
    _name = 'ple.report.inv.bal.09'
    _inherit = 'ple.report.base'

    financial_statements_catalog = fields.Selection(
        selection=[
            ('01', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR DIVERSAS - INDIVIDUAL'),
            ('02', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR SEGUROS - INDIVIDUAL'),
            ('03', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR BANCOS Y FINANCIERAS - INDIVIDUAL'),
            ('04', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - ADMINISTRADORAS DE FONDOS DE PENSIONES (AFP)'),
            ('05', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - AGENTES DE INTERMEDIACIÓN'),
            ('06', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - FONDOS DE INVERSIÓN'),
            ('07', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - PATRIMONIO EN FIDEICOMISOS'),
            ('08', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - ICLV'),
            ('09', 'OTROS NO CONSIDERADOS EN LOS ANTERIORES')
        ],
        string='Catálogo estados financieros',
        default='09',
        required=True
    )
    eeff_presentation_opportunity = fields.Selection(
        selection=[
            ('01', 'Al 31 de diciembre'),
            ('02', 'Al 31 de enero, por modificación del porcentaje'),
            ('03', 'Al 30 de junio, por modificación del coeficiente o porcentaje'),
            ('04',
             'Al último día del mes que sustentará la suspensión o modificación del coeficiente (distinto al 31 de enero o 30 de junio)'),
            ('05',
             'Al día anterior a la entrada en vigencia de la fusión, escisión y demás formas de reorganización de sociedades o emperesas o extinción '
             'de la persona jurídica'),
            ('06', 'A la fecha del balance de liquidación, cierre o cese definitivo del deudor tributario'),
            ('07', 'A la fecha de presentación para libre propósito')
        ],
        string='Oportunidad de presentación de EEFF',
        required=True
    )

    line_ids_309 = fields.One2many(
        comodel_name='ple.report.inv.bal.line.09',
        inverse_name='ple_report_inv_val_09_id',
        string='Líneas'
    )

    xls_filename_309 = fields.Char(string='Filaname Excel 3.9')
    xls_binary_309 = fields.Binary(string='Reporte Excel')
    txt_filename_309 = fields.Char(string='Filename .txt')
    txt_binary_309 = fields.Binary(string='Reporte .TXT 3.9')
    pdf_filename_309 = fields.Char(string='Filename .txt')
    pdf_binary_309 = fields.Binary(string='Reporte .TXT 3.9')

    def name_get(self):
        return [(obj.id, '{} - {}'.format(obj.date_start.strftime('%d/%m/%Y'), obj.date_end.strftime('%d/%m/%Y'))) for
                obj in self]

    def action_generate_excel(self):
        self.line_ids_309.unlink()
        data = self.generate_data_report_309()
        report_xls = ReportInvBalNineExcel(self, data)
        values_content_xls = report_xls.get_content()
        self.xls_binary_309 = base64.b64encode(values_content_xls)
        self.xls_filename_309 = report_xls.get_filename()

        report_txt = ReportInvBalNineTxt(self, data)
        values_content_txt = report_txt.get_content()
        self.txt_binary_309 = base64.b64encode(
            values_content_txt.encode() or '\n'.encode())
        self.txt_filename_309 = report_txt.get_filename()

        report_name = "ple_inv_and_bal_0309.action_print_status_finance"

        pdf = self.env.ref(report_name)._render_qweb_pdf(
            'ple_inv_and_bal_0309.print_status_finance', self.id)[0]
        self.pdf_binary_309 = base64.encodebytes(pdf)
        self.pdf_filename_309 = f"Libro_Activos_Intangibles_{self.date_end.strftime('%Y%m')}.pdf"

    def generate_data_report_309(self):

        query = """
       CREATE OR REPLACE FUNCTION calculate_balance_AMORTIZATION(date_start TIMESTAMP,
                                                                asset_itg INTEGER,
                                                                am_id INTEGER,
                                                                OUT amount_pe FLOAT) AS $$
        BEGIN
        SELECT  sum(aml.balance) into amount_pe
               -- QUERIES TO MATCH MULTI TABLES
                  FROM account_move_line as aml
                  LEFT JOIN account_move am ON  aml.move_id=am.id
                  LEFT JOIN account_account aa on aml.account_id=aa.id
                  LEFT JOIN account_group  ag on aa.group_id=ag.id
              -- FILTER QUERIES 
                  WHERE 
                  aml.asset_intangible_id = asset_itg
                  AND aml.date < date_start
                  AND ag.code_prefix_start = '39'
                  AND aml.balance < 0
                  AND am.id = am_id;
        END;
        $$ 
        LANGUAGE plpgsql;
        
        
        SELECT
        am.name as name_s,
        aml.ple_correlative as ple_correlative,
        aa.ple_selection as ple_selection,
        aa.code as code_account,
        aml.name as name_aml,
        ai.operation_date as operation_date,
        round(sum(aml.balance)) as balance,
        ag.code_prefix_start as code_prefix_start,
        round(COALESCE(calculate_balance_AMORTIZATION('{date_end}',aml.asset_intangible_id,am.id),0)) as balance_amortization,
        round(COALESCE(calculate_balance_AMORTIZATION('{date_start}',aml.asset_intangible_id,am.id),0)) as balance_amortization_xls,
        {ple_report_inv_val_id} as ple_report_inv_val_09_id
        
        
        -- QUERIES TO MATCH MULTI TABLES
        FROM  ACCOUNT_MOVE_LINE aml
         --  TYPE JOIN   |  TABLE               | MATCH
        LEFT JOIN ACCOUNT_MOVE am            ON am.id=aml.move_id
        LEFT JOIN account_account AA         ON aml.account_id = aa.id
        LEFT JOIN asset_intangible AI    ON  aml.asset_intangible_id=ai.id
        LEFT JOIN account_group ag          ON AA.group_id=ag.id
        -- FILTER QUERIES 
        WHERE 
        aa.ple_selection in ('investment_active_intangible_3_9','investment_active_intangible_deprecated_3_9')
        and aa.company_id ='{company_id}'
        and  (('{date_start}' <=aml.date) or   (aml.date < '{date_start}' and ag.code_prefix_start='34'))
        and  aml.date <= '{date_end}' 
      
       
        GROUP BY 
        am.id,aml.id, aa.id,ai.operation_date,ag.code_prefix_start
       """.format(
            company_id=self.company_id.id,
            date_start=self.date_start,
            date_end=self.date_end,
            state='posted',
            financial_statements_catalog=self.financial_statements_catalog,
            date_self=self.date_end.strftime('%Y%m%d'),
            ple_report_inv_val_id=self.id
        )

        try:
            self.env.cr.execute(query)
            values = self.env.cr.dictfetchall()

            for dict in values:
                if dict['balance'] < 0 and dict['ple_selection'] == 'investment_active_intangible_deprecated_3_9':
                    dict.update({'balance_amortization_xls': dict['balance'],
                                 'balance': 0.00,
                                 })

                dict.setdefault('state', '1')
                period = self.date_end.strftime('%Y%m%d')
                dict.setdefault('date', period)
            lines_report = list(values)
            self.env['ple.report.inv.bal.line.09'].create(lines_report)

        except Exception as error:
            raise ValidationError(
                f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

        return values

    def action_close(self):
        self.write({'state': 'closed'})

    def action_rollback(self):
        self.write({'state': 'draft'})
        self.write({
            'txt_binary_309': False,
            'txt_filename_309': False,
            'xls_binary_309': False,
            'xls_filename_309': False,
            'pdf_binary_309': False,
            'pdf_filename_309': False,
            'line_ids_309': False,
        })


class PleInvBalLines09(models.Model):
    _name = 'ple.report.inv.bal.line.09'
    _description = 'Cuentas por cobrar - Líneas'

    ple_report_inv_val_09_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.09',
        string='Reporte de Estado de Situación financiera'
    )
    name = fields.Char()
    ple_correlative = fields.Char()
    ple_selection = fields.Char()
    code_prefix_start = fields.Char()
    initial_balance_amortization = fields.Integer()
    name_aml = fields.Char()
    code_account = fields.Char()
    date = fields.Char()
    balance = fields.Integer()
    balance_amortization = fields.Integer()
    balance_amortization_xls = fields.Integer()
    operation_date = fields.Date()
    state = fields.Char()
    name_s = fields.Char()


class PleInvBal1One(models.Model):
    _inherit = 'ple.report.inv.bal.one'

    m2o_ple_report_inv_bal_09 = fields.Many2one('ple.report.inv.bal.09')
    txt_filename_309 = fields.Char(string='Filaname_09 .txt')
    txt_binary_309 = fields.Binary(string='Reporte .TXT 3.9')
    pdf_filename_309 = fields.Char(string='Filaname_09 .pdf')
    pdf_binary_309 = fields.Binary(string='Reporte .PDF 3.9')
    xls_filename_309 = fields.Char(string='Filaname_09 Excel')
    xls_binary_309 = fields.Binary(string='Reporte Excel')

    def create_book_09(self):
        self.m2o_ple_report_inv_bal_09 = self.env['ple.report.inv.bal.09'].create(
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

        self.m2o_ple_report_inv_bal_09.action_generate_excel()

        self.xls_filename_309 = self.m2o_ple_report_inv_bal_09.xls_filename_309
        self.xls_binary_309 = self.m2o_ple_report_inv_bal_09.xls_binary_309
        self.txt_filename_309 = self.m2o_ple_report_inv_bal_09.txt_filename_309
        self.txt_binary_309 = self.m2o_ple_report_inv_bal_09.txt_binary_309
        self.pdf_filename_309 = self.m2o_ple_report_inv_bal_09.pdf_filename_309
        self.pdf_binary_309 = self.m2o_ple_report_inv_bal_09.pdf_binary_309

        self.m2o_ple_report_inv_bal_09.unlink()

    def action_generate_excel(self):
        self.create_book_09()
        super(PleInvBal1One, self).action_generate_excel()
