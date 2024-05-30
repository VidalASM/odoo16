import base64

from odoo import fields, models
from odoo.exceptions import ValidationError

from datetime import datetime

from ..reports.report_inv_bal_06 import ReportInvBalSixExcel, ReportInvBalSixTxt


class PleReportInvBal06(models.Model):
    _name = 'ple.report.inv.bal.06'
    _description = 'Cuentas por Cobrar Diversas de Terceros y Relacionadas'
    _inherit = 'ple.report.base'

    line_ids = fields.One2many(
        comodel_name='ple.report.inv.bal.line.06',
        inverse_name='ple_report_inv_val_06_id',
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
            ('05', 'Al día anterior a la entrada en vigencia de la fusión, escisión y demás formas de reorganización de sociedades o empresas o extinción de la persona jurídica'),
            ('06', 'A la fecha del balance de liquidación, cierre o cese definitivo del deudor tributario'),
            ('07', 'A la fecha de presentación para libre propósito')
        ],
        string='Oportunidad de presentación de EEFF',
        required=True
    )
    txt_filename = fields.Char(string='Filename .txt')
    txt_binary = fields.Binary(string='Reporte .TXT 3.6')
    pdf_filename = fields.Char(string='Filename .txt')
    pdf_binary = fields.Binary(string='Reporte .TXT 3.6')

    def name_get(self):
        return [(obj.id, '{} - {}'.format(obj.date_start.strftime('%d/%m/%Y'), obj.date_end.strftime('%d/%m/%Y'))) for obj in self]

    def action_generate_report(self):
        self.line_ids.unlink()

        query = """
            SELECT 
                account.id
            FROM account_account AS account
            INNER JOIN account_group AS account_group ON account.group_id = account_group.id
            WHERE 
                account_group.code_prefix_start = '19' and 
                account_group.code_prefix_end = '19'                  
        """

        try:
            self.env.cr.execute(query)
            val_account = self.env.cr.dictfetchall()
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la query, comunicar al administrador: \n {error}')

        if not val_account:
            self.write({'error_dialog': 'No hay cuentas configuradas con Prefijo de código 19'})
            return True

        accounts = []
        for i in val_account:
            accounts.append(i['id'])

        query = """
            SELECT
                LEFT('{period}', 8) as name,

                LEFT(COALESCE(REPLACE(REPLACE(REPLACE(move.name, '/', ''), '-', ''), ' ', ''), ''), 40) as document_name,
                
                LEFT(COALESCE(move_line.ple_correlative, ''), 10) as correlative,
                
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(identification_type_move_doubtful.l10n_pe_vat_code, '')
                ELSE COALESCE(identification_type.l10n_pe_vat_code, '') 
                END, 1) AS type_document_debtor,
                
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(partner_move_doubtful.vat, '') 
                ELSE COALESCE(partner.vat, '') 
                END, 15) AS tax_identification_number,
                            
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(partner_move_doubtful.name, '') 
                ELSE COALESCE(partner.name, '') 
                END, 100) AS business_name,
                
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(document_type_move_doubtful.code, '00') 
                ELSE COALESCE(SPLIT_PART(move_line.name, '.', 1), '00') 
                END, 2) AS type_document,
                
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(SPLIT_PART(REPLACE(move_doubtful.name, ' ', ''), '-', 1), '')
                ELSE COALESCE(SPLIT_PART(move_line.name, '.', 2), '')
                END, 24) AS number_serie,
                
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(SPLIT_PART(REPLACE(move_doubtful.name, ' ', ''), '-', 2), '')
                ELSE COALESCE(SPLIT_PART(move_line.name, '.', 3), '')
                END, 20) AS number_document,
            
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                    THEN COALESCE(TO_CHAR(move_doubtful.invoice_date, 'DD/MM/YYYY'), '')
                    ELSE COALESCE(SPLIT_PART(move_line.name, '.', 4), '')
                END, 10) AS date_of_issue,
                                
                CASE WHEN move_doubtful.id IS NOT NULL 
                THEN move_doubtful.id
                ELSE move.id 
                END AS provisioned_invoice,
                
                UDF_numeric_char(sum(move_line.balance)) as provision_amount,
                
                {ple_report_inv_val_06_id} as ple_report_inv_val_06_id
                            
            FROM account_move_line                    AS move_line
            INNER JOIN account_move                   AS move                              ON move_line.move_id = move.id
            INNER JOIN account_account                AS account                           ON move_line.account_id = account.id
            INNER JOIN account_group                  AS account_group                     ON account.group_id = account_group.id
            LEFT JOIN res_partner                     AS partner                           ON move_line.partner_id = partner.id
            LEFT JOIN l10n_latam_identification_type  AS identification_type               ON partner.l10n_latam_identification_type_id = identification_type.id
            LEFT JOIN account_move                    AS move_doubtful                     ON move.invoice_doubtful_accounts = move_doubtful.id
            LEFT JOIN res_partner                     AS partner_move_doubtful             ON move_doubtful.partner_id = partner_move_doubtful.id
            LEFT JOIN l10n_latam_identification_type  AS identification_type_move_doubtful ON partner_move_doubtful.l10n_latam_identification_type_id = identification_type_move_doubtful.id
            LEFT JOIN l10n_latam_document_type        AS document_type_move_doubtful       ON move_doubtful.l10n_latam_document_type_id = document_type_move_doubtful.id
            
            WHERE 
                account_group.code_prefix_start = '19' AND 
                account_group.code_prefix_end = '19' AND
                move_line.date >= '{date_start}' AND 
                move_line.date <= '{date_end}' AND 
                move_line.company_id = {company_id} AND
                move.state = '{state}' AND
                move_line.account_id in {accounts}
            
            GROUP BY
                document_name, 
                correlative, 
                type_document_debtor, 
                tax_identification_number,
                business_name, 
                type_document, 
                number_serie,
                number_document,
                date_of_issue,
                provisioned_invoice
        """.format(
            period=self.date_end.strftime('%Y%m%d'),
            ple_report_inv_val_06_id=self.id,
            date_start=self.date_start,
            date_end=self.date_end,
            company_id=self.company_id.id,
            state='posted',
            accounts=tuple(accounts)
        )

        try:
            self.env.cr.execute(query)
            values = self.env.cr.dictfetchall()            
            for dict in values:
                dict.setdefault('state', '1')
            lines_report = list(values)
            self.env['ple.report.inv.bal.line.06'].create(lines_report)
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

    def action_generate_excel(self):
        if self.action_generate_report():
            return

        list_data = []
        initial_balances = self.capture_initial_balances_id()
        line_ids = self.env['ple.report.inv.bal.line.06'].search([('ple_report_inv_val_06_id', '=', self.id)], order='name asc')
        for obj_line in line_ids:
            exist_initial = obj_line.provisioned_invoice in initial_balances
            if exist_initial:
                initial = initial_balances.get(obj_line.provisioned_invoice)
                credit_temp = abs(float(obj_line.provision_amount) + float(initial['provision_amount']))
                real_credit = float(obj_line.provision_amount) + float(initial['provision_amount'])
                initial_balances.pop(obj_line.provisioned_invoice)
            else:
                credit_temp = abs(float(obj_line.provision_amount))
                real_credit = float(obj_line.provision_amount)

            values = {
                'name': obj_line.name,
                'document_name': obj_line.document_name,
                'correlative': obj_line.correlative,
                'type_document_debtor': obj_line.type_document_debtor,
                'tax_identification_number': obj_line.tax_identification_number,
                'business_name': obj_line.business_name,
                'type_document': obj_line.type_document,
                'number_serie': obj_line.number_serie,
                'number_document': obj_line.number_document,
                'date_of_issue': obj_line.date_of_issue,
                'provisioned_invoice': obj_line.provisioned_invoice,
                'provision_amount': credit_temp,
                'real_credit': real_credit,
                'state': obj_line.state
            }
            list_data.append(values)

        if len(initial_balances) > 0:
            for obj_initial in initial_balances.keys():
                data = initial_balances.get(obj_initial)
                values = {
                    'name': data['name'],
                    'document_name': data['document_name'],
                    'correlative': data['correlative'],
                    'type_document_debtor': data['type_document_debtor'],
                    'tax_identification_number': data['tax_identification_number'],
                    'business_name': data['business_name'],
                    'type_document': data['type_document'],
                    'number_serie': data['number_serie'],
                    'number_document': data['number_document'],
                    'date_of_issue': data['date_of_issue'],
                    'provisioned_invoice': data['provisioned_invoice'],
                    'provision_amount': data['provision_amount'],
                    'state': data['state']
                }
                list_data.append(values)

        self.write({'line_final_ids': [(5, 0, 0)]})
        for ending_balances in list_data:
            self.write({
                'line_final_ids': [
                    (0, 0, {
                        'name': ending_balances['name'],
                        'document_name': ending_balances['document_name'],
                        'correlative': ending_balances['correlative'],
                        'type_document_debtor': ending_balances['type_document_debtor'],
                        'tax_identification_number': ending_balances['tax_identification_number'],
                        'business_name': ending_balances['business_name'],
                        'type_document': ending_balances['type_document'],
                        'number_serie': ending_balances['number_serie'],
                        'number_document': ending_balances['number_document'],
                        'date_of_issue': ending_balances['date_of_issue'],
                        'provisioned_invoice': ending_balances['provisioned_invoice'],
                        'provision_amount': ending_balances['provision_amount'],
                        'state': ending_balances['state'],
                        'ple_report_inv_val_06_id': self.id,
                    }),
                ]
            })

        report_xls = ReportInvBalSixExcel(self, list_data)
        report_txt = ReportInvBalSixTxt(self, list_data)

        values_content_xls = report_xls.get_content()
        values_content_txt = report_txt.get_content()

        data = {
            'txt_binary': base64.b64encode(values_content_txt.encode() or '\n'.encode()),
            'txt_filename': report_txt.get_filename(),
            'error_dialog': 'No hay contenido para presentar en el registro de ventas electrónicos de este periodo.' if not values_content_txt else False,
            'xls_binary': base64.b64encode(values_content_xls),
            'xls_filename': report_xls.get_filename(),
            'date_ple': fields.Date.today(),
            'state': 'load'
        }

        self.write(data)

        for rec in self:
            report_name = "ple_inv_and_bal_0306.action_print_status_finance"
            pdf = self.env.ref(report_name)._render_qweb_pdf('ple_inv_and_bal_0306.print_status_finance', self.id)[0]

            rec.pdf_binary = base64.encodebytes(pdf)
            year, month, day = self.date_end.strftime('%Y/%m/%d').split('/')
            rec.pdf_filename = f'Libro_Estimación cobranza dudosa_{year}{month}.pdf'

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


class PleReportInvBalLine06(models.Model):
    _name = 'ple.report.inv.bal.line.06'
    _description = 'Ple Report Inv Bal Line 06'
    _order = 'name desc'

    name = fields.Char(string='Periodo')
    document_name = fields.Char(string='CUO')
    correlative = fields.Char(string='Correlativo')
    type_document_debtor = fields.Char(string='Tipo de documento del deudor')
    tax_identification_number = fields.Char(string='Número de documento deudor')
    business_name = fields.Char(string='Razon social del deudor')
    type_document = fields.Char(string='Tipo de CPE de la cuenta por cobrar')
    number_serie = fields.Char(string='Número de serie del comprobante de pago')
    number_document = fields.Char(string='Número del comprobante de pago')
    date_of_issue = fields.Char(string='Fecha de emisión del comprobante de pago')
    provisioned_invoice = fields.Char(string='Factura provisionada')
    provision_amount = fields.Float(string='Monto de la provisión')
    state = fields.Char(string='Indica el estado de la operación')
    ple_report_inv_val_06_id = fields.Many2one(comodel_name='ple.report.inv.bal.06', string='Reporte PLE 0306')
