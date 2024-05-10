import ast

from datetime import datetime

from odoo import models, fields
from odoo.exceptions import ValidationError


class SireSaleBase(models.AbstractModel):
    _name = 'sire.sale.base'
    _description = 'Sire Sale Base'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañia',
        required=True,
        default=lambda self: self.env.company
    )
    year = fields.Selection(
        selection=[
            (str(year), str(year)) for year in range(2010, (datetime.now().year) + 1)
        ],
        string='Año',
        required=True
    )
    month = fields.Selection(
        selection=[
            ('01', 'Enero'),
            ('02', 'Febrero'),
            ('03', 'Marzo'),
            ('04', 'Abril'),
            ('05', 'Mayo'),
            ('06', 'Junio'),
            ('07', 'Julio'),
            ('08', 'Agosto'),
            ('09', 'Setiembre'),
            ('10', 'Octubre'),
            ('11', 'Noviembre'),
            ('12', 'Diciembre')
        ],
        string='Periodo',
        required=True
    )
    xlsx_filename = fields.Char(string='Nombre del archivo Excel')
    xlsx_binary = fields.Binary(string='Reporte Excel')
    zip_filename = fields.Char(string='Nombre del archivo TXT')
    zip_binary = fields.Binary(string='Reporte TXT')
    error_dialog = fields.Text(readonly=True)

    def _select_sire_sale(self):
        return f"""
            LEFT(COALESCE('{self.company_id.vat}', ''), 11) AS company_vat,
            LEFT(COALESCE(company.name, ''), 1500) AS company_name,
            LEFT(COALESCE('{self.year}{self.month}', ''), 6) AS period,
            LEFT(COALESCE(TO_CHAR(account_move.invoice_date, 'DD/MM/YYYY'), ''), 10) AS invoice_date,
            LEFT(COALESCE(document_type.code, ''), 2) AS document_type_code,
            LEFT(COALESCE(REPLACE(REPLACE(REPLACE(account_move.name, '/', ''), ' ', ''), '-', ''), ''), 40) AS invoice_name,
            LEFT(COALESCE(
                (
                    SELECT account_move_line.ple_correlative
                    FROM account_move_line AS account_move_line
                    INNER JOIN account_account AS account_account ON account_move_line.account_id = account_account.id
                    WHERE
                        account_move_line.move_id = account_move.id
                        AND account_account.account_type = 'asset_receivable'
                    ORDER BY
                        ABS(
                            EXTRACT(YEAR FROM AGE(account_move_line.date_maturity, account_move.invoice_date)) * 12 +
                            EXTRACT(MONTH FROM AGE(account_move_line.date_maturity, account_move.invoice_date))
                        ) DESC
                    LIMIT 1
                ), ''
            ), 10) AS invoice_line_correlative,
            LEFT(COALESCE(SPLIT_PART(REPLACE(account_move.name, ' ', ''), '-', 1), ''), 20) AS invoice_serie,
            CASE 
                WHEN document_type.code IN ('01', '02', '03', '07', '08') and account_move.name IS NOT NULL THEN 
                    LPAD(LEFT(COALESCE(SPLIT_PART(REPLACE(account_move.name, ' ', ''), '-', 2), ''), 20), 8, '0') 
                ELSE 
                    LEFT(COALESCE(SPLIT_PART(REPLACE(account_move.name, ' ', ''), '-', 2), ''), 20) 
            END AS invoice_correlative,
            LEFT(COALESCE(identification_type.l10n_pe_vat_code, ''), 1) AS partner_identification_code,
            LEFT(COALESCE(partner.vat, ''), 15) AS partner_vat,
            validate_string(partner.name, 1500) AS partner_name,
            get_tax(account_move.id, account_move.move_type, COALESCE(document_type.code, '')) AS tax_data,
            LEFT(COALESCE(currency.name, ''), 3) AS currency_name,
            CASE 
                WHEN currency.name = 'PEN' THEN 
                    1 
                ELSE 
                    ROUND(account_move.exchange_rate, 3) 
            END AS exchange_rate,
            LEFT(COALESCE(TO_CHAR(account_move.origin_invoice_date, 'DD/MM/YYYY'), ''), 10) AS origin_invoice_date,
            LEFT(COALESCE(origin_document_type.code, ''), 2) AS origin_document_type_code,
            LEFT(COALESCE(SPLIT_PART(REPLACE(account_move.origin_number, ' ', ''), '-', 1), ''), 20) AS origin_number_serie,
            LEFT(COALESCE(SPLIT_PART(REPLACE(account_move.origin_number, ' ', ''), '-', 2), ''), 20) AS origin_number_correlative,
            CASE WHEN account_move.bool_pay_invoice IS NOT NULL THEN '1' ELSE '' END AS bool_pay_invoice,
            LEFT(COALESCE(account_move.ple_state, ''), 1) AS ple_state,
            CASE WHEN account_move.l10n_pe_edi_operation_type IN ('1001', '1002', '1003', '1004') THEN 'TieneDetraccion' ELSE '' END AS detraction
        """

    def _from_sire_sale(self):
        return """
            account_move                             AS account_move
            INNER JOIN res_partner                   AS partner              ON account_move.partner_id = partner.id
            INNER JOIN res_company                   AS company              ON account_move.company_id = company.id
            INNER JOIN res_currency                  AS currency             ON account_move.currency_id = currency.id
            LEFT JOIN l10n_latam_document_type       AS origin_document_type ON account_move.origin_l10n_latam_document_type_id = origin_document_type.id
            LEFT JOIN l10n_latam_document_type       AS document_type        ON account_move.l10n_latam_document_type_id = document_type.id
            LEFT JOIN l10n_latam_identification_type AS identification_type  ON partner.l10n_latam_identification_type_id = identification_type.id
        """

    def _where_sire_sale(self):
        return f"""
            (
                (
                    account_move.company_id = {self.company_id.id}
                    AND account_move.move_type IN ('out_invoice', 'out_refund')
                )
                AND (
                    DATE_PART('year', account_move.ple_date) = {self.year}
                    AND DATE_PART('month', account_move.ple_date) = {self.month}
                )
                AND (
                    account_move.state NOT IN ('draft')
                    OR account_move.state IS NULL
                )
                AND (
                    account_move.journal_id IN (
                        SELECT journal.id
                        FROM account_journal AS journal
                        WHERE (
                            journal.ple_no_include IS NULL
                            OR journal.ple_no_include = false
                        )
                        AND (
                            journal.company_id IS NULL
                            OR journal.company_id IN ({self.company_id.id})
                        )
                        ORDER BY journal.id
                    )
                )
                AND (
                    account_move.journal_id IN (
                        SELECT journal.id
                        FROM account_journal AS journal
                        WHERE (
                            journal.type = 'sale'
                        )
                        AND (
                            journal.company_id IS NULL
                            OR journal.company_id IN ({self.company_id.id})
                        )
                        ORDER BY journal.id
                    )
                )
                AND (
                    account_move.ple_its_declared IS NULL
                    OR account_move.ple_its_declared = false
                )
            )
        """

    def _group_by_sire_sale(self):
        return ""

    def _order_by_sire_sale(self):
        return """
            account_move.date DESC,
            account_move.name DESC,
            account_move.id DESC
        """

    def _query_sire_sale(self):
        group_by_ = self._group_by_sire_sale()
        return f"""
            SELECT {self._select_sire_sale()}
            FROM {self._from_sire_sale()}
            WHERE {self._where_sire_sale()}
            {"GROUP BY" + group_by_ if group_by_ else ""}
            ORDER BY {self._order_by_sire_sale()}
        """

    def _execute_query_sire_sale(self):
        try:
            self.env.cr.execute(self._query_sire_sale())
            return self.env.cr.dictfetchall()
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la consulta, contacte al administrador: \n {error}')

    def _process_query_results(self):
        query_results = self._execute_query_sire_sale()
        for line_result in query_results:
            tax_data = ast.literal_eval(line_result['tax_data'])
            line_result.update({
                's_base_exp': tax_data[0],
                's_base_og': tax_data[1],
                's_base_ogd': tax_data[2],
                's_tax_og': tax_data[3],
                's_tax_ogd': tax_data[4],
                's_base_oe': tax_data[5],
                's_base_ou': tax_data[6],
                's_tax_isc': tax_data[7],
                's_tax_icbp': tax_data[8],
                's_base_ivap': tax_data[9],
                's_tax_ivap': tax_data[10],
                's_tax_other': tax_data[11],
                'amount_total': tax_data[12]
            })
        return query_results
