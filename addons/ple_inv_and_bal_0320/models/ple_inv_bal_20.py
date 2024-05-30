from odoo import fields, models
from odoo.exceptions import ValidationError
from ..reports.report_inv_bal_20 import ReportInvBal20Excel, ReportInvBal20Txt
import base64

class PleInvBal20(models.Model):
    _name = 'ple.report.inv.bal.20'
    _description = 'Statement of income'
    _inherit = 'ple.report.base'

    line_ids = fields.One2many(
        comodel_name='ple.report.inv.bal.line.20',
        inverse_name='ple_report_inv_val_20_id',
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

    txt_filename = fields.Char(
        string='Filaname .txt'
    )
    txt_binary = fields.Binary(
        string='Reporte .TXT 3.20'
    )
    pdf_filename = fields.Char(
        string='Reporte .PDF 3.20'
    )
    pdf_binary = fields.Binary(
        string='Reporte .PDF 3.20'
    )

    def action_generate_report(self):
        self.line_ids.unlink()
        account_query = """
                SELECT account_account.id
                 -- QUERIES TO MATCH MULTI TABLES
                    FROM eeff_ple
                --  TYPE JOIN   |  TABLE                        | MATCH
                    INNER JOIN   account_account                ON account_account.eerr_ple_id = eeff_ple.id
                -- FILTER QUERIES 
                    WHERE eeff_ple.eeff_type = '3.20';                    
        """
        self.env.cr.execute(account_query)
        val_account = self.env.cr.dictfetchall()

        if not val_account:
            self.write({'error_dialog': 'No hay cuentas configuradas con tipo 3.20 EERR'})
            return True

        acc_q = []
        for i in val_account:
            if len(val_account) > 1:
                acc_q.append(i['id'])
            else:
                acc_q.append(0)
                acc_q.append(i['id'])

        query = """
        SELECT
                eeff_ple.sequence as sequence,
                '{date_self}' as name,
                '{financial_statements_catalog}' as catalog_code,
                eeff_ple.code as financial_state_code,
                eeff_ple.id as eerr_ple_id,
                eeff_ple.id as parent,
                eeff_ple.description as description,
                UDF_numeric_char(sum(account_move_line.balance)) as credit,
                {ple_report_inv_val_id} as ple_report_inv_val_20_id
            -- QUERIES TO MATCH MULTI TABLES
                FROM account_move_line 
            --  TYPE JOIN   |  TABLE                        | MATCH
                INNER JOIN    account_account               ON account_move_line.account_id = account_account.id
                INNER JOIN    eeff_ple                      ON eeff_ple.id = account_account.eerr_ple_id
            -- FILTER QUERIES 
                WHERE eeff_ple.eeff_type = '3.20' and 
                account_move_line.date <= '{date_end}' and ((account_move_line.date >= '{date_start}') OR 
                "account_move_line"."account_id" in( SELECT "account_account".id FROM "account_account"
                 WHERE ("account_account"."include_initial_balance" = False)))
                and account_move_line.company_id = {company_id} and  ("account_move_line"."account_id" in {accounts})
                and account_move_line.parent_state = '{state}'
                GROUP BY
                    eeff_ple.sequence, eeff_ple.code, eeff_ple.id, eeff_ple, parent;
        """.format(
            company_id=self.company_id.id,
            date_start=self.date_start,
            date_end=self.date_end,
            state='posted',
            financial_statements_catalog=self.financial_statements_catalog,
            date_self=self.date_end.strftime('%Y%m%d'),
            accounts=tuple(acc_q),
            ple_report_inv_val_id=self.id
        )

        try:
            self.env.cr.execute(query)
            values = self.env.cr.dictfetchall()

            for dict in values:
                dict.setdefault('state', '1')
            
            lines_data = {}
            for dict in values:
                self.check_key_in_dicts(dict['eerr_ple_id'], lines_data, dict)
                self.check_parent_lines(dict['parent'], dict['credit'], lines_data)

            lines_report = list(lines_data.values())

            for data in lines_report:
                if len(data) == 10:
                    del data['parent']
            self.env['ple.report.inv.bal.line.20'].create(lines_report)

        except Exception as error:
            raise ValidationError(f'Error al ejecutar la query, comunicar al administrador: \n {error}')

    def check_parent_lines(self, eerr_ple_id, credit, list_data):
        if isinstance(eerr_ple_id, int):
            eeff_ple_data = self.env['eeff.ple'].search([('id', '=', eerr_ple_id)])
        else:
            eeff_ple_data = eerr_ple_id
        parent_ids = eeff_ple_data.parent_ids
        if not parent_ids:
            return
        else:
            for parent_id in parent_ids:
                parent_values = {
                    'sequence': parent_id.sequence,
                    'description': parent_id.description,
                    'name': self.date_end.strftime('%Y%m%d') or '',
                    'catalog_code': self.financial_statements_catalog,
                    'financial_state_code': parent_id.code or '',
                    'eerr_ple_id': parent_id.id or False,
                    'parent': parent_id.id or False,
                    'credit': credit,
                    'state': '1',
                    'ple_report_inv_val_20_id': self.id
                }
                self.check_key_in_dicts(parent_id.id, list_data, parent_values)
                self.check_parent_lines(parent_id, credit, list_data)

    def check_key_in_dicts(self, key_val, list_data, new_data):
        if key_val not in list_data.keys():
            list_data.setdefault(key_val, new_data)
        else:
            new_credit = float(list_data[key_val]['credit']) + float(new_data['credit'])
            list_data[key_val]['credit'] = self.env['ple.report.base'].check_decimals(new_credit)

    def action_generate_excel(self):
        if self.action_generate_report():
            return
        list_data = []
        line_ids = self.env['ple.report.inv.bal.line.20'].search([('ple_report_inv_val_20_id', '=', self.id)],
                                                                 order='sequence asc')
        for obj_line in line_ids:
            credit_temp = abs(float(obj_line.credit))
            real_credit = float(obj_line.credit)

            values = {
                'name': obj_line.name,
                'description': obj_line.description,
                'catalog_code': obj_line.catalog_code,
                'financial_state_code': obj_line.financial_state_code,
                'credit': round(credit_temp, 2),
                'state': obj_line.state,
                'sequence': obj_line.sequence,
                'eerr_ple_id': obj_line.eerr_ple_id,
                'account_ids': obj_line.account_ids,
                'real_credit': round(real_credit, 2),
            }
            list_data.append(values)

        report_txt = ReportInvBal20Txt(self, list_data)
        report_xls = ReportInvBal20Excel(self, list_data)

        values_content = report_txt.get_content()
        values_content_xls = report_xls.get_content()

        data = {
            'txt_binary': base64.b64encode(values_content.encode() or '\n'.encode()),
            'txt_filename': report_txt.get_filename(),
            'error_dialog': 'No hay contenido para presentar en el registro de este periodo.' if not values_content else False,
            'xls_binary': base64.b64encode(values_content_xls),
            'xls_filename': report_xls.get_filename(),
            'date_ple': fields.Date.today(),
            'state': 'load'
        }
        self.write(data)

        for rec in self:
            report_name = "ple_inv_and_bal_0320.action_print_status_finance"
            pdf = self.env.ref(report_name)._render_qweb_pdf('ple_inv_and_bal_0320.print_status_finance', self.id)[0]
            rec.pdf_binary = base64.encodebytes(pdf)
            year, month, day = self.date_end.strftime('%Y/%m/%d').split('/')
            rec.pdf_filename = f'Libro_Estado de Resultados_{year}{month}.pdf'

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
            'line_ids': False,
        })


class PleInvBalLines20(models.Model):
    _name = 'ple.report.inv.bal.line.20'
    _description = 'Estado de Resultados - Líneas'
    _order = 'sequence desc'

    name = fields.Char(
        string='Periodo'
    )
    sequence = fields.Integer(
        string='Secuencia'
    )
    ple_report_inv_val_20_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.20',
        string='Reporte de Estado de Resultados'
    )
    catalog_code = fields.Char(
        string='Código de catálogo'
    )
    financial_state_code = fields.Char(
        string='Código del Rubro del Estado Financiero'
    )
    eerr_ple_id = fields.Many2one(
        string='Rubro EERR PLE',
        comodel_name='eeff.ple'
    )
    credit = fields.Char(
        string='Saldo del Rubro Contable'
    )
    state = fields.Char(
        string='Indica el estado de la operación'
    )
    account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Cuentas',
        readonly=1
    )
    description = fields.Char(
        string='Descripción'
    )
