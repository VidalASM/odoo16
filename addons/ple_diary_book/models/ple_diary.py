import base64
import datetime
from odoo import fields, models
from ..reports.report_diary import DiaryReportExcel, DiaryReportTxt
from odoo.exceptions import ValidationError


class PleDiary(models.Model):
    _name = 'ple.report.diary'
    _description = 'Report PLE Registro Diario'
    _inherit = 'ple.report.base'

    xls_filename_diary = fields.Char()
    xls_binary_diary = fields.Binary(string='Reporte Excel - Libro diario')
    txt_filename_diary = fields.Char()
    txt_binary_diary = fields.Binary(string='Reporte TXT 5.1')
    txt_filename_diary1 = fields.Char()
    txt_binary_diary1 = fields.Binary(string='Reporte TXT Plan de cuentas con valores 5.3')
    txt_filename_diary2 = fields.Char()
    txt_binary_diary2 = fields.Binary(string='Reporte TXT Plan de cuentas sin valores 5.3')
    txt_filename_diary3 = fields.Char()
    txt_binary_diary3 = fields.Binary(string='Reporte TXT 5.2 Diario simplificado')
    txt_filename_diary4 = fields.Char()
    txt_binary_diary4 = fields.Binary(string='Reporte TXT Plan de cuentas con valores 5.4')
    txt_filename_diary5 = fields.Char()
    txt_binary_diary5 = fields.Binary(string='Reporte TXT Plan de cuentas sin valores 5.4')

    error_dialog_5_3 = fields.Text(readonly=True)


    def action_generate_excel(self):
        query_aml = """
                SELECT
                TO_CHAR(account_move_line.date, 'YYYYMM00') as period_name,
                replace(replace(replace(account_move_line__move_id.name, '/', ''), '-', ''), ' ', '') as move_name,
                (SELECT get_journal_correlative(res_company.ple_type_contributor, account_move_line.ple_correlative)
                        FROM account_move 
                        INNER JOIN res_company ON account_move.company_id = res_company.id
                        WHERE account_move.id = account_move_line__move_id.id LIMIT 1
                ) as correlative_line,
                coalesce(trim(replace(replace(replace(account_account.code, '/', ''), '-', ''), '.', '')), '') as account_code, 
                coalesce(res_currency.name, 'PEN') as currency_name,
                coalesce(l10n_latam_identification_type.l10n_pe_vat_code, '') as partner_document_type_code,
                coalesce(res_partner.vat, '') as partner_document_number,
                TO_CHAR(account_move_line__move_id.date, 'DD/MM/YYYY') as move_date,
                validate_string(string_ref(coalesce(coalesce(account_move_line__move_id.ref, account_move_line.name), '')), 200) as reference,
                string_ref(validate_string(coalesce(account_move_line.name, ''), 200)) as move_line_name,
                CASE 
                  WHEN account_journal.type = 'sale' AND move_type IN ('out_invoice', 'out_refund') THEN
                    LEFT(COALESCE(replace(split_part(replace(account_move_line.serie_correlative, ' ', ''), '-', 1), '-', '0000'), LEFT(COALESCE(replace(split_part(replace(account_move_line.move_name, ' ', ''), '-', 1), '-', '0000'), ''), 4)), 4)
                  WHEN account_journal.type = 'purchase' AND move_type IN ('in_invoice', 'in_refund') THEN
                    LEFT(COALESCE(replace(split_part(replace(account_move_line.serie_correlative, ' ', ''), '-', 1), '-', '0000'), LEFT(COALESCE(replace(split_part(replace(account_move_line.ref, ' ', ''), '-', 1), '-', '0000'), ''), 4)), 4)
                  WHEN account_journal.type IN ('cash', 'bank', 'general') AND move_type = 'entry' THEN
                    LEFT(COALESCE(replace(split_part(replace(account_move_line.serie_correlative, ' ', ''), '-', 1), '-', '0000'), ''), 4)
                  ELSE '0000'
                END AS invoice_serie,                
                CASE 
                  WHEN account_journal.type = 'sale' AND move_type IN ('out_invoice', 'out_refund') THEN
                    LEFT(COALESCE(replace(split_part(replace(account_move_line.serie_correlative, ' ', ''), '-', 2), '-', '00000000'), LEFT(COALESCE(replace(split_part(replace(account_move_line.move_name, ' ', ''), '-', 2), '-', '00000000'), ''), 8) ), 8)
                  WHEN account_journal.type = 'purchase' AND move_type IN ('in_invoice', 'in_refund') THEN
                    LEFT(COALESCE(replace(split_part(replace(account_move_line.serie_correlative, ' ', ''), '-', 2), '-', '00000000'), LEFT(COALESCE(replace(split_part(replace(account_move_line.ref, ' ', ''), '-', 2), '-', '00000000'), ''), 8) ), 8)
                  WHEN account_journal.type IN ('cash', 'bank', 'general') AND move_type = 'entry' THEN
                    LEFT(COALESCE(replace(split_part(replace(account_move_line.serie_correlative, ' ', ''), '-', 2), '-', '00000000'), ''), 8)
                  ELSE '00000000'
                END AS invoice_correlative,                             
                validate_string(COALESCE(split_part(replace(account_move_line__move_id.name, ' ', ''), '-', 1), '0000'),20) AS invoice_serie_oo,
                coalesce(left(split_part(replace(account_move_line__move_id.name, ' ', ''), '-', 2),20),'') AS invoice_correlative_oo,
                coalesce(TO_CHAR(account_move_line__move_id.invoice_date_due, 'DD/MM/YYYY'), '') as invoice_date_due,
                coalesce(l10n_latam_document_type.code, '00') AS invoice_document_type_code,
                account_move_line__move_id.move_type as move_type,
                account_move_line__move_id.ref as reference,
                account_move_line.name as ml_name,
                account_move_line.id as aml_id,
                to_json(account_move_line.analytic_distribution) as analytic_distribution2,
                account_move_line__move_id.name as ml_name2,
                account_move_line__move_id.payment_reference as payment_reference,
                account_move_line.debit as debit,
                account_move_line.credit as credit,
                CASE 
                    WHEN 
                        account_move_line__move_id.date <= '2023-09-30'
                    THEN 
                        (
                            SELECT get_data_structured_diary(
                                account_journal.type, 
                                account_journal.ple_no_include, 
                                account_move.is_nodomicilied, 
                                account_move.name, 
                                account_move.date
                            ) 
                            FROM account_move
                            LEFT JOIN account_journal ON account_move.journal_id = account_journal.id
                            WHERE account_move.id = account_move_line__move_id.id
                        )
                    ELSE
                        (
                            SELECT get_data_structured_sire(
                                account_journal.type, 
                                account_journal.ple_no_include, 
                                account_move.is_nodomicilied, 
                                account_move.name, 
                                account_move.ref,
                                '{company_vat}', 
                                res_partner.vat,
                                coalesce(l10n_latam_document_type.code, '00')
                            ) 
                            FROM account_move
                            LEFT JOIN account_journal ON account_move.journal_id = account_journal.id
                            WHERE account_move.id = account_move_line__move_id.id
                        )                
                END AS data_structured
                -- QUERIES TO MATCH MULTI TABLES
                FROM "account_move" as "account_move_line__move_id","account_move_line"
                --  TYPE JOIN   |  TABLE                        | MATCH
                    INNER JOIN  account_account                ON account_move_line.account_id = account_account.id
                    LEFT JOIN   res_currency                   ON account_move_line.currency_id = res_currency.id
                    LEFT JOIN   res_partner                    ON account_move_line.partner_id = res_partner.id
                    LEFT JOIN   account_journal                ON account_move_line.journal_id = account_journal.id
                    LEFT JOIN   l10n_latam_document_type       ON account_move_line.l10n_latam_document_type_id = l10n_latam_document_type.id
                    LEFT JOIN   l10n_latam_identification_type ON res_partner.l10n_latam_identification_type_id = l10n_latam_identification_type.id
                -- FILTER QUERIES                    
                WHERE ("account_move_line"."move_id"="account_move_line__move_id"."id") AND
                        (((((("account_move_line"."date" >= '{date_start}')  AND
                        ("account_move_line"."date" <= '{date_end}'))  AND
                        ("account_move_line"."company_id" = {company_id}))  AND
                        "account_move_line"."move_id" IS NOT NULL)  AND
                        ("account_move_line__move_id"."state" = '{state}'))  AND
                        "account_move_line"."account_id" IS NOT NULL) AND
                        ("account_move_line"."company_id" IS NULL   OR
                        ("account_move_line"."company_id" in ({company_id})))
                -- ORDER DATA
                ORDER BY "account_move_line"."date" DESC,"account_move_line"."move_name" DESC,"account_move_line"."id"
        """.format(
            company_id=self.company_id.id,
            company_vat=self.company_id.vat,
            date_start=self.date_start,
            date_end=self.date_end,
            state='posted',
            ple_report_diary_id=self.id
        )

        query_account = """
                SELECT 
                TO_CHAR(account_account.ple_date_account, 'YYYYMMDD') as period_name,
                coalesce(trim(replace(replace(replace(account_account.code, '/', ''), '-', ''), '.', '')), '') as account_code,
                coalesce(trim(substring(account_account.name, 1, 99)), '') as account_name,
                coalesce(res_company.code_prefix, '') as code_prefix,
                coalesce(trim(substring(account_group.name, 1, 59)), '') as name_group,
                coalesce(account_account.ple_state_account, '') as state_account
                -- QUERIES TO MATCH MULTI TABLES
                FROM "account_account" 
                --  TYPE JOIN    |  TABLE                   | MATCH
                    INNER JOIN      res_company           ON account_account.company_id = res_company.id
                    LEFT JOIN       account_group         ON account_account.group_id = account_group.id
                -- FILTER QUERIES
                WHERE ("account_account"."company_id" IS NULL   OR  ("account_account"."company_id" in ({company_id})))
                -- ORDER DATA
                ORDER BY "account_account"."code"
        """.format(
            company_id=self.company_id.id
        )

        try:
            self.env.cr.execute(query_aml)
            data_aml = self.env.cr.dictfetchall()
            self.env.cr.execute(query_account)
            data_account = self.env.cr.dictfetchall()
            self.action_generate_report(data_aml, data_account)
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la query, comunicarse con el administrador: \n {error}')

    def action_generate_report(self, data_aml, data_account):
        list_data = []
        account_analytic_data = list(map(lambda x: (x.id,x.name), self.env['account.analytic.account'].search([])))
        date_limit = datetime.date(2023,9,30)
        for obj_move_line in data_aml:
            ml_name = obj_move_line.get('ml_name', '') or obj_move_line.get('ml_name2', '')

            if obj_move_line.get('move_type') in ('entry', 'in_invoice', 'in_refund', 'in_receipt'):
                reference = obj_move_line.get('reference', '') or ml_name
            else:
                reference = obj_move_line.get('payment_reference', '') or ml_name

            move_name = obj_move_line.get('move_name', '')
            analytic_distribution2 =obj_move_line.get('analytic_distribution2').keys() if obj_move_line.get('analytic_distribution2') else ''
            nueva_lista = list(map(lambda clave: [elemento[1] for elemento in account_analytic_data if str(elemento[0]) == clave][0] if any(str(elemento[0]) == clave for elemento in account_analytic_data) else None, list(analytic_distribution2)))

            data_structured = obj_move_line.get('data_structured', '') if self.date_end <= date_limit else ''

            values_move = {
                'period_name': obj_move_line.get('period_name', ''),
                'move_name': move_name,
                'correlative_line': obj_move_line.get('correlative_line', ''),
                'account_code': obj_move_line.get('account_code', ''),
                'currency_name': obj_move_line.get('currency_name', ''),
                'analytic_distribution': ', '.join(nueva_lista),
                'partner_document_type_code': obj_move_line.get('partner_document_type_code', ''),
                'partner_document_number': obj_move_line.get('partner_document_number', ''),
                'move_date': obj_move_line.get('move_date', ''),
                'reference': reference.replace('\n', ' ')[:200],
                'move_line_name': ml_name.replace('\n', ' ')[:200],
                'invoice_serie': obj_move_line.get('invoice_serie', ''),
                'invoice_correlative': obj_move_line.get('invoice_correlative', ''),
                'invoice_date_due': obj_move_line.get('invoice_date_due', ''),
                'invoice_document_type_code': obj_move_line.get('invoice_document_type_code', ''),
                'debit': "{0:.2f}".format(obj_move_line.get('debit', '')),
                'credit': "{0:.2f}".format(obj_move_line.get('credit')),
                'data_structured': data_structured,
                'state': '1',
            }

            if values_move.get('invoice_document_type_code') == '':
                values_move.update({'invoice_document_type_code': '00'})

            if values_move.get('invoice_serie') == '':
                values_move.update({'invoice_serie': '00000000'})

            if values_move.get('invoice_correlative') == '':
                values_move.update({'invoice_correlative': '0000'})

            list_data.append(values_move)

        list_account = []
        for obj_account_line in data_account:
            values_account = {
                'period_name': obj_account_line.get('period_name', ''),
                'account_code': obj_account_line.get('account_code', ''),
                'account_name': obj_account_line.get('account_name', ''),
                'code_prefix': obj_account_line.get('code_prefix', ''),
                'name_group': obj_account_line.get('name_group', '').replace('\n', ''),
                'state_account': obj_account_line.get('state_account', ''),
            }
            list_account.append(values_account)

        diary_report = DiaryReportTxt(self, list_data, list_account)

        values_content = diary_report.get_content()
        report_values = {
            'txt_binary_diary': base64.b64encode(values_content and values_content.encode() or '\n'.encode()),
            'txt_filename_diary': diary_report.get_filename(),
            'txt_binary_diary3': base64.b64encode(values_content and values_content.encode() or '\n'.encode()),
            'txt_filename_diary3': diary_report.get_filename(3),
        }
        if not values_content:
            report_values['error_dialog'] = '- No hay contenido para presentar en el registro de libro diario 5.1 electrónico de este periodo. \n' \
                                            '- No hay contenido para presentar en el registro de libro diario 5.2 electrónico de este periodo. '
        else:
            report_values['error_dialog'] = ''

        values_content1 = diary_report.get_content(1)
        report_values.update({
            'txt_binary_diary1': base64.b64encode(values_content1 and values_content1.encode() or '\n'.encode()),
            'txt_filename_diary1': diary_report.get_filename(1),
            'txt_binary_diary4': base64.b64encode(values_content1 and values_content1.encode() or '\n'.encode()),
            'txt_filename_diary4': diary_report.get_filename(4),
        })

        if not values_content1:
            report_values['error_dialog_5_3'] = '- No hay contenido para presentar en el registro de libro diario 5.3 electrónico de este periodo. \n' \
                                                '- No hay contenido para presentar en el registro de libro diario 5.4 electrónico de este periodo.'
        else:
            report_values['error_dialog_5_3'] = ''

        values_content2 = diary_report.get_content(2)
        report_values.update({
            'txt_binary_diary2': base64.b64encode(values_content2 and values_content2.encode() or '\n'.encode()),
            'txt_filename_diary2': diary_report.get_filename(2),
            'txt_binary_diary5': base64.b64encode(values_content2 and values_content2.encode() or '\n'.encode()),
            'txt_filename_diary5': diary_report.get_filename(5)
        })

        diary_report_xls = DiaryReportExcel(self, list_data)
        values_content_xls = diary_report_xls.get_content()

        report_values.update({
            'xls_binary_diary': base64.b64encode(values_content_xls),
            'xls_filename_diary': diary_report_xls.get_filename(),
            'date_ple': fields.Date.today(),
            'state': 'load',
        })
        self.write(report_values)

    def action_close(self):
        super(PleDiary, self).action_close()

    def action_rollback(self):
        super(PleDiary, self).action_rollback()
        self.write({
            'xls_filename_diary': False,
            'xls_binary_diary': False,
            'txt_binary_diary': False,
            'txt_filename_diary': False,
            'txt_binary_diary1': False,
            'txt_filename_diary1': False,
            'txt_binary_diary2': False,
            'txt_filename_diary2': False,
            'txt_binary_diary3': False,
            'txt_filename_diary3': False,
            'txt_binary_diary4': False,
            'txt_filename_diary4': False,
            'txt_binary_diary5': False,
            'txt_filename_diary5': False,
        })
