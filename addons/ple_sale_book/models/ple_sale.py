import ast
import base64

from odoo.exceptions import ValidationError

from odoo import fields, models
from ..reports.sale_report import SaleReportExcel, SaleReportTxt


class PleReportSale(models.Model):
    _name = 'ple.report.sale'
    _description = 'PLE Sales Record Report'
    _inherit = 'ple.report.base'

    move_ids = fields.Many2many(
        comodel_name='account.move',
        string='Facturas relacionadas'
    )

    def action_generate_excel(self):
        query = """
                    SELECT
                    TO_CHAR(am.date, 'YYYYMM00') AS period,
                    replace(replace(replace(am.name, '/', ''), '-', ''), ' ', '') AS number_origin,
                    (SELECT
                        CASE
                            WHEN company.ple_type_contributor = 'CUO' THEN
                                (SELECT COALESCE(ple_correlative, 'M000000001') FROM account_move_line where move_id = am.id LIMIT 1)
                            WHEN company.ple_type_contributor = 'RER' THEN 'M-RER'
                            ELSE ''
                        END
                    ) AS journal_correlative,
                    TO_CHAR(am.invoice_date, 'DD/MM/YYYY') AS date_invoice,
                    CASE WHEN document_type.code is not null AND document_type.code = '14' AND am.state != 'cancel' THEN
                        TO_CHAR(am.invoice_date_due, 'DD/MM/YYYY') ELSE ''
                    END AS date_due,
                    COALESCE(document_type.code, '') AS voucher_sunat_code,
                    split_part(replace(am.name, ' ', ''), '-', 1) AS voucher_series,
                    split_part(replace(am.name, ' ', ''), '-', 2) AS correlative,
                    COALESCE(identification_type.l10n_pe_vat_code, '') AS customer_document_type,
                    COALESCE(partner.vat, '') AS customer_document_number,
                    validate_string(partner.name, 99) AS customer_name,
                    get_tax(am.id, am.move_type, COALESCE(document_type.code, '')) AS tax_data,
                    currency.name AS code_currency,
                    ROUND(am.exchange_rate, 3) AS currency_rate,
                    COALESCE(TO_CHAR(am.origin_invoice_date, 'DD/MM/YYYY'), '') AS origin_date_invoice,
                    COALESCE(origin_document_type.code, '') AS origin_document_code,
                    split_part(replace(COALESCE(am.origin_number, ''), ' ', ''), '-', 1) AS origin_serie,
                    split_part(replace(COALESCE(am.origin_number, ''), ' ', ''), '-', 2) AS origin_correlative,
                    COALESCE(am.ple_state, '') AS ple_state,
                    am.id AS invoice_id,
                    {ple_report_sale_id} AS ple_report_sale_id
                    -- QUERIES TO MATCH MULTI TABLES
                    FROM account_move am
                    --  TYPE JOIN |  TABLE                         | VARIABLE                    | MATCH
                        INNER JOIN  "res_partner"                    partner                       ON   am.partner_id = partner.id
                        INNER JOIN  "res_company"                    company                       ON   am.company_id = company.id
                        INNER JOIN  "res_currency"                   currency                      ON   am.currency_id = currency.id
                        LEFT JOIN   "l10n_latam_document_type"       origin_document_type          ON   am.origin_l10n_latam_document_type_id = origin_document_type.id
                        LEFT JOIN   "l10n_latam_document_type"       document_type                 ON   am.l10n_latam_document_type_id = document_type.id
                        LEFT JOIN   "l10n_latam_identification_type" identification_type           ON   partner.l10n_latam_identification_type_id = identification_type.id
                    WHERE
                    -- FILTER QUERIES
                    ((((((((am."company_id" = {company_id}) AND
                            (am."move_type" in ('{move_type1}','{move_type2}'))) AND
                            (am."ple_date" >= '{date_start}')) AND
                            (am."ple_date" <= '{date_end}')) AND
                            ((am."state" not in ('{state}')) OR am."state" IS NULL)) AND
                            (am."journal_id" in (SELECT "account_journal".id FROM "account_journal" WHERE
                                                            ("account_journal"."ple_no_include" IS NULL or "account_journal"."ple_no_include" = false ) AND
                                                            ("account_journal"."company_id" IS NULL  OR ("account_journal"."company_id" in ({company_id})))
                                                            ORDER BY  "account_journal"."id"  ))) AND
                            (am."journal_id" in (SELECT "account_journal".id FROM "account_journal" WHERE ("account_journal"."type" = '{journal_type}') AND
                                                            ("account_journal"."company_id" IS NULL  OR ("account_journal"."company_id" in ({company_id})))
                                                            ORDER BY  "account_journal"."id"  ))) AND
                            (am."ple_its_declared" IS NULL or am."ple_its_declared" = false )) AND
                            (am."company_id" IS NULL  OR (am."company_id" in ({company_id})))
                    -- ORDER DATA
                    ORDER BY  am."date" DESC,am."name" DESC,am."id" DESC
                """.format(
            company_id=self.company_id.id,
            move_type1='out_invoice',
            move_type2='out_refund',
            date_start=self.date_start,
            date_end=self.date_end,
            state='draft',
            journal_type='sale',
            ple_report_sale_id=self.id
        )
        try:
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
            self.get_excel_data(result)
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la query, comunicarse con el administrador: \n {error}')

    def get_excel_data(self, data_lines):
        list_data = []
        invoices = []
        for obj_line in data_lines:
            tax_data = ast.literal_eval(obj_line['tax_data'])
            obj_line.update({
                'amount_export': tax_data[0],
                'amount_untaxed': tax_data[1],
                'discount_tax_base': tax_data[2],
                'sale_no_gravadas_igv': tax_data[3],
                'discount_igv': tax_data[4],
                'amount_exonerated': tax_data[5],
                'amount_no_effect': tax_data[6],
                'isc': tax_data[7],
                'tax_icbp': tax_data[8],
                'rice_tax_base': tax_data[9],
                'rice_igv': tax_data[10],
                'another_taxes': tax_data[11],
                'amount_total': tax_data[12],
            })
            value = {
                'period': obj_line.get('period', ''),
                'number_origin': obj_line.get('number_origin', ''),
                'journal_correlative': obj_line.get('journal_correlative', ''),
                'date_invoice': obj_line.get('date_invoice', ''),
                'date_due': obj_line.get('date_due', ''),
                'voucher_sunat_code': obj_line.get('voucher_sunat_code', ''),
                'voucher_series': obj_line.get('voucher_series', ''),
                'correlative': obj_line.get('correlative', ''),
                'correlative_end': '',
                'customer_document_type': obj_line.get('customer_document_type', ''),
                'customer_document_number': obj_line.get('customer_document_number', ''),
                'customer_name': obj_line.get('customer_name', ''),
                'amount_export': obj_line.get('amount_export', ''),
                'amount_untaxed': obj_line.get('amount_untaxed', ''),
                'discount_tax_base': obj_line.get('discount_tax_base', ''),
                'sale_no_gravadas_igv': obj_line.get('sale_no_gravadas_igv', ''),
                'discount_igv': obj_line.get('discount_igv', ''),
                'amount_exonerated': obj_line.get('amount_exonerated', ''),
                'amount_no_effect': obj_line.get('amount_no_effect', ''),
                'isc': obj_line.get('isc', ''),
                'rice_tax_base': obj_line.get('rice_tax_base', ''),
                'tax_icbp': "{0:.2f}".format(obj_line.get('tax_icbp', '')),
                'rice_igv': obj_line.get('rice_igv', ''),
                'another_taxes': obj_line.get('another_taxes', ''),
                'amount_total': round(float(obj_line.get('amount_export', '')) + float(obj_line.get('amount_untaxed', '')) + float(
                    obj_line.get('discount_tax_base', '')) + float(obj_line.get('sale_no_gravadas_igv', '')) + float(obj_line.get('discount_igv', '')) + float(
                    obj_line.get('amount_exonerated', '')) + float(obj_line.get('amount_no_effect', '')) + float(obj_line.get('rice_tax_base', '')) + float(
                    obj_line.get('tax_icbp', '')) + float(obj_line.get('rice_igv', '')) + float(obj_line.get('another_taxes', '')), 2),
                'code_currency': obj_line.get('code_currency', ''),
                'currency_rate': "{0:.3f}".format(obj_line.get('currency_rate', '')),
                'origin_date_invoice': obj_line.get('origin_date_invoice', ''),
                'origin_document_code': obj_line.get('origin_document_code', ''),
                'origin_serie': obj_line.get('origin_serie', ''),
                'origin_correlative': obj_line.get('origin_correlative', ''),
                'contract_name': obj_line.get('contract_name', ''),
                'inconsistency_type_change': obj_line.get('inconsistency_type_change', ''),
                'payment_voucher': obj_line.get('payment_voucher', ''),
                'ple_state': obj_line.get('ple_state', ''),
            }
            list_data.append(value)
            invoices.append(obj_line['invoice_id'])

        sale_report = SaleReportTxt(self, list_data)
        values_content = sale_report.get_content()

        sale_report_xls = SaleReportExcel(self, list_data)
        values_content_xls = sale_report_xls.get_content()
        self.write({
            'txt_binary': base64.b64encode(values_content.encode() or '\n'.encode()),
            'txt_filename': sale_report.get_filename(),
            'error_dialog': 'No hay contenido para presentar en el registro de ventas electrónicos de este periodo.' if not values_content else '',
            'xls_binary': base64.b64encode(values_content_xls),
            'xls_filename': sale_report_xls.get_filename(),
            'date_ple': fields.Date.today(),
            'state': 'load',
            'move_ids': invoices
        })

    def action_close(self):
        super(PleReportSale, self).action_close()
        for move in self.move_ids:
            move.write({'ple_its_declared': False})

    def action_rollback(self):
        super(PleReportSale, self).action_rollback()
        self.write({
            'txt_binary': False,
            'txt_filename': False,
            'xls_binary': False,
            'xls_filename': False,
            'move_ids': False
        })
