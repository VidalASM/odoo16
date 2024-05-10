from odoo import fields, models, api
from ..reports.report_inv_bal_16_02 import ReportInvBalSixteen02Excel, ReportInvBalSixteen02Txt
import base64


class PleInvBal1602(models.Model):
    _name = 'ple.report.inv.bal.16.2'
    _description = 'Estructura de la participación accionaria o de participaciones sociales'
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

    txt_filename = fields.Char(string='Filename .txt')
    txt_binary = fields.Binary(string='Reporte .TXT 3.16.1')

    def action_generate_excel(self):
        self.ensure_one()
        data = self.company_id.lines_report_0316.search([('is_member', '=', True), ('id', 'in', self.company_id.lines_report_0316.ids)])
        report_xls = ReportInvBalSixteen02Excel(self, data)
        values_content_xls = report_xls.get_content()
        self.xls_binary = base64.b64encode(values_content_xls)
        self.xls_filename = report_xls.get_filename()

        report_txt = ReportInvBalSixteen02Txt(self, data)
        values_content_txt = report_txt.get_content()
        self.txt_binary = base64.b64encode(values_content_txt.encode() or '\n'.encode())
        self.txt_filename = report_txt.get_filename()

    def action_close(self):
        self.write({'state': 'closed'})

    def action_rollback(self):
        self.write({'state': 'draft'})
        self.write({
            'txt_binary': False,
            'txt_filename': False,
            'xls_binary': False,
            'xls_filename': False,
            'pdf_binary': False,
            'pdf_filename': False,
            'line_final_ids': False,
            'line_ids': False,
        })
