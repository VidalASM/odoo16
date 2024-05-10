from odoo import fields, models, api
from ..reports.report_inv_bal_04 import ReportInvBalFourExcel, ReportInvBalFourTxt
import base64


class PleInvBal104(models.Model):
    _name = 'ple.report.inv.bal.04'
    _description = 'Cuentas por cobrar'
    _inherit ='ple.report.base'

    line_ids = fields.One2many(
        comodel_name='ple.report.inv.bal.line.04',
        inverse_name='ple_report_inv_val_04_id',
        string='Líneas'
    )
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
            ('04', 'Al último día del mes que sustentará la suspensión o modificación del coeficiente (distinto al 31 de enero o 30 de junio)'),
            ('05', 'Al día anterior a la entrada en vigencia de la fusión, escisión y demás formas de reorganización de sociedades o emperesas o extinción '
                   'de la persona jurídica'),
            ('06', 'A la fecha del balance de liquidación, cierre o cese definitivo del deudor tributario'),
            ('07', 'A la fecha de presentación para libre propósito')
        ],
        string='Oportunidad de presentación de EEFF',
        required=True
    )

    total_mount = fields.Float()

    txt_filename = fields.Char(string='Filaname .txt')
    txt_binary = fields.Binary(string='Reporte .TXT 3.4')

    pdf_filename = fields.Char(string='Filaname .txt')
    pdf_binary = fields.Binary(string='Reporte .TXT 3.4')

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, f"{rec.date_start.strftime('%d/%m/%Y')} - {rec.date_end.strftime('%d/%m/%Y')}"))
        return res

    def action_generate_report(self):
        total_mount_04 = 0.00
        self.line_ids.unlink()
        account_ids = self.env['account.account'].search([('group_id.code_prefix_start', '=', '14')])
        wizard = self.env['wizard.report.financial'].create({
            'date_start': self.date_start,
            'date_end': self.date_end,
            'account_ids': account_ids,
        })
        data = wizard.generate_data()
        lines_data = []
        lines_data_no = []
        check = False
        for k in data.keys():
            if data[k]:
                for x in data[k]:
                    space_a = k.index(' ')
                    if len(lines_data) == 0:
                        values = {
                            'account': x['account'],
                            'desc_account': k[space_a:],
                            'period': self.date_end.strftime('%Y%m%d') or '',
                            'code_uo': x['move'],
                            'doc_num': x['vat_ple'],
                            'name_client': x['partner_ple'],
                            'date_ref': x['date'],
                            'mont': x['balance'],
                            'status': '1',
                            'ple_report_inv_val_04_id': self.id,
                            'valor': 1,
                        }
                        if 'ple_correlative' in x.keys():
                            values['correlative'] = x['ple_correlative']                        
                        if 'l10n_latam_identification_type_id' in x.keys():
                            doc_type = x['l10n_latam_identification_type_id']
                            doc_type = doc_type.l10n_pe_vat_code if doc_type else ''
                            values['doc_type'] = doc_type
                        if x['vat'] == '0':
                            values['doc_type'] = 0
                        if values['mont'] == 0:
                            values['mont'] = 0.00
                        total_mount_04 = total_mount_04 + x['balance']
                        lines_data.append(values)
                    else:

                        values = {
                            'account': x['account'],
                            'desc_account': k[space_a:],
                            'period': self.date_end.strftime('%Y%m%d') or '',
                            'code_uo': x['move'],
                            'doc_num': x['vat_ple'],
                            'name_client': x['partner_ple'],
                            'date_ref': x['date'],
                            'mont': x['balance'],
                            'status': '1',
                            'ple_report_inv_val_04_id': self.id,
                            'valor': 1,
                        }
                        if 'ple_correlative' in x.keys():
                            values['correlative'] = x['ple_correlative']                        
                        if 'l10n_latam_identification_type_id' in x.keys():
                            doc_type = x['l10n_latam_identification_type_id']
                            doc_type = doc_type.l10n_pe_vat_code if doc_type else ''
                            values['doc_type'] = doc_type
                        if x['vat'] == '0':
                            values['doc_type'] = 0
                        if values['mont'] != 0:
                            lines_data.append(values)
                        total_mount_04 = total_mount_04 + x['balance']

        for z in data.keys():
            if data[z]:
                for x in data[z]:
                    space_a = z.index(' ')
                    if len(lines_data_no) == 0:
                        values = {
                            'account': x['account'],
                            'desc_account': z[space_a:],
                            'period': self.date_end.strftime('%Y%m%d') or '',
                            'code_uo': x['move'],
                            'doc_num': x['vat_ple'],
                            'name_client': x['partner_ple'],
                            'date_ref': x['date'],
                            'mont': x['balance'],
                            'status': '1',
                            'ple_report_inv_val_04_id': self.id,
                            'valor': 2,
                        }
                        if 'ple_correlative' in x.keys():
                            values['correlative'] = x['ple_correlative']                        
                        if 'l10n_latam_identification_type_id' in x.keys():
                            doc_type = x['l10n_latam_identification_type_id']
                            doc_type = doc_type.l10n_pe_vat_code if doc_type else ''
                            values['doc_type'] = doc_type
                        if x['vat'] == '0':
                            values['doc_type'] = 0
                        if values['mont'] == 0:
                            values['mont'] = 0.00
                        lines_data_no.append(values)
                    else:
                        values = {
                            'account': x['account'],
                            'desc_account': z[space_a:],
                            'period': self.date_end.strftime('%Y%m%d') or '',
                            'code_uo': x['move'],
                            'doc_num': x['vat_ple'],
                            'name_client': x['partner_ple'],
                            'date_ref': x['date'],
                            'mont': x['balance'],
                            'status': '1',
                            'ple_report_inv_val_04_id': self.id,
                            'valor': 2,
                        }
                        if 'ple_correlative' in x.keys():
                            values['correlative'] = x['ple_correlative']                        
                        if 'l10n_latam_identification_type_id' in x.keys():
                            doc_type = x['l10n_latam_identification_type_id']
                            doc_type = doc_type.l10n_pe_vat_code if doc_type else ''
                            values['doc_type'] = doc_type
                        if x['vat'] == '0':
                            values['doc_type'] = 0
                        if values['mont'] != 0:
                            lines_data_no.append(values)

        self.env['ple.report.inv.bal.line.04'].create(lines_data_no)
        self.total_mount = total_mount_04
        self.env['ple.report.inv.bal.line.04'].create(lines_data)

    def action_generate_excel(self):
        self.action_generate_report()
        list_data = []
        list_data_no = []
        for obj_line in self.line_ids:
            if obj_line.valor == 1:
                values = {
                    'account': obj_line.account,
                    'desc_account': obj_line.desc_account,
                    'period': obj_line.period,
                    'code_uo': obj_line.code_uo.replace('/', '').replace('-', '').replace(' ', ''),
                    'correlative': obj_line.correlative,
                    'doc_type': obj_line.doc_type,
                    'doc_num': obj_line.doc_num,
                    'name_client': obj_line.name_client,
                    'date_ref': obj_line.date_ref,
                    'mont': obj_line.mont,
                    'status': obj_line.status
                }
                list_data.append(values)
            if obj_line.valor == 2:
                values = {
                    'account': obj_line.account,
                    'desc_account': obj_line.desc_account,
                    'period': obj_line.period,
                    'code_uo': obj_line.code_uo.replace('/', '').replace('-', '').replace(' ', ''),
                    'correlative': obj_line.correlative,
                    'doc_type': obj_line.doc_type,
                    'doc_num': obj_line.doc_num,
                    'name_client': obj_line.name_client,
                    'date_ref': obj_line.date_ref,
                    'mont': obj_line.mont,
                    'status': obj_line.status
                }
                list_data_no.append(values)

        report_excel = ReportInvBalFourExcel(self, list_data_no)
        report_txt = ReportInvBalFourTxt(self, list_data)

        values_content_excel = report_excel.get_content()
        values_content_txt = report_txt.get_content()

        data = {
            'txt_binary': base64.b64encode(values_content_txt.encode() or '\n'.encode()),
            'txt_filename': report_txt.get_filename(),
            'error_dialog': 'No hay contenido para presentar en el registro de ventas electrónicos de este periodo.' if not values_content_txt else False,
            'xls_binary': base64.b64encode(values_content_excel),
            'xls_filename': report_excel.get_filename(),
            'date_ple': fields.Date.today(),
            'state': 'load'
        }

        self.write(data)

        for rec in self:
            report_name = "ple_inv_and_bal_0304.action_print_status_finance"
            pdf = self.env.ref(report_name)._render_qweb_pdf('ple_inv_and_bal_0304.print_status_finance', self.id)[0]
            rec.pdf_binary = base64.encodebytes(pdf)
            year, month, day = self.date_end.strftime('%Y/%m/%d').split('/')
            rec.pdf_filename = f'Libro_Cuentas por cobrar Acc. y Pers_{year}{month}.pdf'

    def action_close(self):
        self.write({'state': 'closed'})

    def action_rollback(self):
        self.write({'state': 'draft'})
        self.write({
            'total_mount': False,
            'txt_filename': False,
            'txt_binary': False,
            'pdf_filename': False,
            'pdf_binary': False,
            'xls_binary': False,
        })


class PleInvBalLines(models.Model):
    _name = 'ple.report.inv.bal.line.04'
    _description = 'Cuentas por cobrar - Líneas'
    _order = 'sequence desc'

    account = fields.Float(string="Nro Cuenta")
    desc_account = fields.Char(string="Descripcion")
    period = fields.Char(string="Periodo")
    code_uo = fields.Char(string="Codigo unico de operacion")
    correlative = fields.Char(string="Numero correlativo")
    doc_type = fields.Char(string="Tipo de Documento")
    doc_num = fields.Char(string="Numero de documento")
    name_client = fields.Char(string="Apellido y Nombres, Den. o Raz. Social cliente")
    date_ref = fields.Char(string="Fecha de Referencia")
    mont = fields.Float(string="Monto de Cuenta por Cobrar")
    status = fields.Char(string="Estado")

    note = fields.Char(string="Nota")
    valor = fields.Float(string='Valor')

    sequence = fields.Float(string='Secuencia')

    ple_report_inv_val_04_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.04',
        string='Reporte de Estado de Situación financiera'
    )