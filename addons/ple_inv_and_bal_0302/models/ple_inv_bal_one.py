from odoo import fields, models, api
from odoo.exceptions import ValidationError
from ..reports.report_inv_bal_one import ReportInvBalOneExcel, ReportInvBalOneTxt
import base64


class PleInvBal1One(models.Model):
    _name = 'ple.report.inv.bal.one'
    _description = 'Efectivo y Equivalente de efectivo'
    _inherit = {'ple.report.base': 'ple_id'}

    line_ids = fields.One2many(
        comodel_name='ple.report.inv.bal.line.one',
        inverse_name='ple_report_inv_val_one_id',
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

    txt_filename = fields.Char(string='Filaname .txt')
    txt_binary = fields.Binary(string='Reporte .TXT 3.2')
    pdf_filename = fields.Char(string='Reporte .PDF 3.2')
    pdf_binary = fields.Binary(string='Reporte .PDF 3.2')

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, f"{rec.date_start.strftime('%d/%m/%Y')} - {rec.date_end.strftime('%d/%m/%Y')}"))
        return res

    def action_generate_excel(self):
        company_id = self.company_id.id
        date_start = self.date_start
        date_end = self.date_end

        account_ids = """
            SELECT
                account_account.id,
                group_id,
                account_account.code,
                account_account.name,
                res_currency.name AS type_currency,
                sunat_bank_code,
                acc_number
            
            -- QUERIES TO MATCH MULTI TABLES      
            FROM account_account
            
            --  TYPE JOIN   |  TABLE                        | MATCH
                INNER JOIN      account_group               ON (account_group.id = account_account.group_id)
                LEFT JOIN       res_partner_bank            ON (account_account.bank_id = res_partner_bank.id)
                LEFT JOIN       res_bank                    ON (res_partner_bank.bank_id = res_bank.id)
                LEFT JOIN       res_currency                ON (account_account.currency_id = res_currency.id)
            
            -- FILTER QUERIES 
            WHERE account_group.code_prefix_start = '10'
                AND account_account.company_id IS NOT NULL
            """

        group_10 = f"""
            SELECT
                account_id, 
                account_move_line.balance
            -- QUERIES TO MATCH MULTI TABLES
            FROM account_move as am, account_move_line
          
            -- FILTER QUERIES 
            WHERE(account_move_line.move_id = am.id)
            AND(
                    (
                        (
                            ((account_move_line.date <= '{date_end}' and ((account_move_line.date >= '{date_start}') OR 
                                    "account_move_line"."account_id" in( SELECT "account_account".id FROM "account_account"
                                     WHERE ("account_account"."include_initial_balance" = True)))))
                        AND  (account_move_line.company_id = {company_id}))
                    AND am.state = 'posted')
                AND(account_move_line.account_id in (SELECT ids.id FROM ({account_ids}) AS ids)))
            AND(account_move_line.company_id IS NULL OR(account_move_line.company_id in ({company_id})))
            """

        query = f"""
            SELECT
                SUM(group_10.balance) AS balance,
                replace(lines.code, '.', '') AS accounting_account,
                lines.name AS bank_account_name,
                CASE WHEN replace(lines.code, '.', '')  IN ('1030001', '1051000', '1051002') THEN
                    lines.type_currency
                    ELSE (
                        CASE WHEN lines.type_currency IS NOT NULL THEN                    
                            lines.type_currency
                            ELSE 'PEN'
                        END
                    )
                END AS type_currency,
                CASE WHEN lines.sunat_bank_code IS NOT NULL THEN
                    lines.sunat_bank_code ELSE '99'        
                END AS bic,
                CASE WHEN lines.sunat_bank_code != '99' THEN
                    lines.acc_number ELSE '-'
                END AS account_bank_code
        
            -- QUERIES TO MATCH MULTI TABLES
            FROM (({account_ids}) AS lines 
        
            --  TYPE JOIN               |  TABLE                        | MATCH    
                INNER JOIN ({group_10}) AS group_10                     ON lines.id = group_10.account_id)
        
            -- GROUP DATA
            GROUP BY
                lines.name,
                lines.type_currency,
                lines.sunat_bank_code,
                lines.acc_number,
                accounting_account
            """

        try:

            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
            ids = (self.env['ple.report.inv.bal.line.one'].create(result)).ids
            self.line_ids = ids
            self.get_excel_data(result)

        except Exception as error:
            raise ValidationError(f'Error al ejecutar queries, comunciar al administrador: \n {error}')

    def get_excel_data(self, data_lines):
        list_data = []
        initial_balances = self.capture_initial_balances_id()

        for obj_line in data_lines:
            exist_initial = obj_line['accounting_account'] in initial_balances

            if exist_initial:
                initial = initial_balances.get(obj_line['accounting_account'])
                obj_line['balance'] += initial['balance']
                initial_balances.pop(obj_line['accounting_account'])

            if obj_line['balance'] != 0.00 and obj_line['bic']:
                values = {
                    'period': self.date_end.strftime('%Y%m%d') or '',
                    'accounting_account': obj_line['accounting_account'],
                    'bank_account_name': obj_line['bank_account_name'],
                    'type_currency': obj_line['type_currency'],
                    'balance': obj_line['balance'],
                    'credit_balance': -obj_line['balance'] if obj_line['balance'] <= 0.00 else 0.00,
                    'debit_balance': obj_line['balance'] if obj_line['balance'] > 0.00 else 0.00,
                    'status': '1',
                    'bic': obj_line['bic'],
                    'account_bank_code': obj_line['account_bank_code'],
                }
                list_data.append(values)

        if len(initial_balances) > 0:
            for obj_initial in initial_balances.keys():
                data = initial_balances.get(obj_initial)
                if data['balance'] != 0.00:
                    values = {
                        'period': self.date_end.strftime('%Y%m%d') or '',
                        'accounting_account': obj_initial,
                        'bank_account_name': data['bank_account_name'],
                        'type_currency': data['type_currency'],
                        'balance': data['balance'],
                        'credit_balance': data['balance'] if data['balance'] <= 0.00 else 0.00,
                        'debit_balance': data['balance'] if data['balance'] > 0.00 else 0.00,
                        'status': '1',
                        'bic': data['bic'],
                        'account_bank_code': data['account_bank_code'],
                        'ple_report_inv_val_one_id': data['ple_report_inv_val_one_id'],
                    }
                    list_data.append(values)

        self.write({
            'line_final_ids': [(5, 0, 0)],
        })

        for ending_balances in list_data:
            self.write({
                'line_final_ids': [
                    (0, 0, {'period': self.date_end.strftime('%Y%m%d') or '',
                            'accounting_account': ending_balances['accounting_account'],
                            'bank_account_name': ending_balances['bank_account_name'],
                            'type_currency': ending_balances['type_currency'],
                            'balance':ending_balances['balance'],
                            'status': '1',
                            'bic': ending_balances['bic'],
                            'account_bank_code': ending_balances['account_bank_code'],
                            'ple_report_inv_val_one_id': self.id,
                            }),
                ]
            })


        report_excel = ReportInvBalOneExcel(self, list_data)
        report_txt = ReportInvBalOneTxt(self, list_data)

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

        # add report pdf
        report_name = "ple_inv_and_bal_0302.action_print_status_finance_0302"
        pdf = self.env.ref(report_name)._render_qweb_pdf('ple_inv_and_bal_0302.print_status_finance_0302',self.id)[0]
        self.pdf_binary = base64.encodebytes(pdf)
        year, month, day = self.date_end.strftime('%Y/%m/%d').split('/')
        self.pdf_filename = f'Libro_Efectivo y equivalente de efectivo_{year}{month}.pdf'

    def action_close(self):
        self.write({'state': 'closed'})

    def action_rollback(self):
        self.write({'state': 'draft'})


class PleInvBalLines(models.Model):
    _name = 'ple.report.inv.bal.line.one'
    _description = 'Efectivo y Equivalente de efectivo - Líneas'
    _order = 'sequence desc'

    period = fields.Char(string="Periodo")
    accounting_account = fields.Char(string="Cuenta contables")
    bank_account_name = fields.Char(string="Nombre de la cuenta bancaria")
    type_currency = fields.Char(string="Tipo de Moneda")
    balance = fields.Float(string="Saldo")
    credit_balance = fields.Float(string="Saldo acreedor", compute="_onchange_credit_balance")
    debit_balance = fields.Float(string="Saldo Deudor", compute="_onchange_debit_balance")
    status = fields.Char(string="Estado")
    note = fields.Char(string="Nota")
    bic = fields.Char(string="Codigo de la Entidad Financiera")
    account_bank_code = fields.Char(string="Número de la cuenta de la Entidad Financiera")
    sequence = fields.Integer(string='Secuencia')

    ple_report_inv_val_one_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.one',
        string='Reporte de Estado de Situación financiera'
    )

    account_ids = fields.Many2many(
        comodel_name='account.move.line',
        string='Cuentas',
        readonly=1
    )

    @api.depends('balance')
    def _onchange_credit_balance(self):
        for record in self:
            record.credit_balance = record.balance if record.balance <= 0.00 else 0.00

    @api.depends('balance')
    def _onchange_debit_balance(self):
        for record in self:
            record.debit_balance = record.balance if record.balance > 0.00 else 0.00