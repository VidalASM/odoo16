import ast

from datetime import datetime

from odoo import models, fields
from odoo.exceptions import ValidationError


class SirePurchaseBase(models.AbstractModel):
    _name = 'sire.purchase.base'
    _description = 'Sire Purchase Base'

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

    def _select_sire_purchase(self):
        return f"""
            LEFT(COALESCE('{self.company_id.vat}', ''), 11) AS company_vat,
            LEFT(COALESCE(company.name, ''), 1500) AS company_name,
            LEFT(COALESCE('{self.year}{self.month}', ''), 6) AS period,
            LEFT(COALESCE(TO_CHAR(account_move.invoice_date, 'DD/MM/YYYY'), ''), 10) AS invoice_date,
            CASE 
                WHEN document_type.code IN ('14', '46', '50', '51', '52', '53', '54') THEN 
                    LEFT(COALESCE(TO_CHAR(account_move.invoice_date_due, 'DD/MM/YYYY'), ''), 10) 
                ELSE 
                    '' 
            END AS invoice_date_due,
            LEFT(COALESCE(document_type.code, ''), 2) AS document_type_code,
            LEFT(COALESCE(REPLACE(REPLACE(REPLACE(account_move.name, '/', ''), ' ', ''), '-', ''), ''), 40) AS invoice_name,
            COALESCE(account_move.ref, '') AS ref,
            LEFT(COALESCE(
                (
                    SELECT account_move_line.ple_correlative
                    FROM account_move_line AS account_move_line
                    INNER JOIN account_account AS account_account ON account_move_line.account_id = account_account.id
                    WHERE
                        account_move_line.move_id = account_move.id
                        AND account_account.account_type = 'liability_payable'
                    ORDER BY
                        ABS(
                            EXTRACT(YEAR FROM AGE(account_move_line.date_maturity, account_move.invoice_date)) * 12 +
                            EXTRACT(MONTH FROM AGE(account_move_line.date_maturity, account_move.invoice_date))
                        ) DESC
                    LIMIT 1
                ), ''
            ), 10) AS invoice_line_correlative,
            CASE 
                WHEN document_type.code IN ('46') and account_move.ref IS NOT NULL THEN 
                    LPAD(LEFT(COALESCE(SPLIT_PART(REPLACE(account_move.ref, ' ', ''), '-', 1), ''), 20), 4, '0') 
                ELSE 
                    LEFT(COALESCE(SPLIT_PART(REPLACE(account_move.ref, ' ', ''), '-', 1), ''), 20)
            END AS ref_serie,
            LEFT(COALESCE(account_move.year_aduana, ''), 4) AS year_aduana,
            CASE 
                WHEN document_type.code IN ('01', '02', '03', '07', '08') and account_move.ref IS NOT NULL THEN 
                    LPAD(LEFT(COALESCE(SPLIT_PART(REPLACE(account_move.ref, ' ', ''), '-', 2), ''), 20), 8, '0') 
                ELSE 
                    LEFT(COALESCE(SPLIT_PART(REPLACE(account_move.ref, ' ', ''), '-', 2), ''), 20) 
            END AS ref_correlative,
            LEFT(COALESCE(TO_CHAR(account_move.voucher_payment_date, 'DD/MM/YYYY'), ''), 10) AS voucher_payment_date,
            CASE 
                WHEN account_move.igv_withholding_indicator = true THEN 
                    '1' 
                ELSE 
                    '' 
            END AS igv_withholding_indicator,
            LEFT(COALESCE(account_move.voucher_number, ''), 24) AS voucher_number,
            LEFT(COALESCE(account_move.inv_serie, ''), 20) AS inv_serie,
            LEFT(COALESCE(account_move.inv_year_dua_dsi, ''), 4) AS inv_year_dua_dsi,
            LEFT(COALESCE(account_move.inv_correlative, ''), 20) AS inv_correlative,
            COALESCE(CAST(TO_CHAR(account_move.inv_retention_igv, '9999999999D99') AS DECIMAL(9,2)), '0.00') AS inv_retention_igv,
            LEFT(COALESCE(country.l10n_pe_sunat_code, ''), 4) AS country_code,
            LEFT(COALESCE(identification_type.l10n_pe_vat_code, ''), 1) AS partner_identification_code,
            LEFT(COALESCE(partner.vat, ''), 15) AS partner_vat,
            validate_string(partner.name, 1500) AS partner_name,
            LEFT(COALESCE(link_economic.code, ''), 2) AS linkage_code,
            get_tax_purchase(account_move.id, account_move.move_type) AS tax_data,
            COALESCE(TO_CHAR(account_move.hard_rent, '9999999999D99'), '0.00') AS hard_rent,
            COALESCE(TO_CHAR(account_move.deduccion_cost, '9999999999D99'), '0.00') AS deduccion_cost,
            COALESCE(TO_CHAR(account_move.neto_rent, '9999999999D99'), '0.00') AS neto_rent,
            COALESCE(TO_CHAR(account_move.retention_rate, '9999999999D99'), '0.00') AS retention_rate,
            COALESCE(TO_CHAR(account_move.tax_withheld, '9999999999D99'), '0.00') AS tax_withheld,
            LEFT(COALESCE(account_move.cdi, ''), 2) AS cdi,
            LEFT(COALESCE(TO_CHAR(exoneration_nodomicilied.code, '99999999'), ''), 1) AS exoneration_nodomicilied_code,
            LEFT(COALESCE(type_rent.code, ''), 2) AS type_rent_code,
            LEFT(COALESCE(service_taken.code, ''), 1) AS taken_code,
            CASE 
                WHEN account_move.application_article IS NOT NULL THEN 
                    '1' 
                ELSE 
                    '' 
            END AS application_article,
            LEFT(COALESCE(currency.name, ''), 3) AS currency_name,
            CASE 
                WHEN currency.name = 'PEN' THEN 
                    NULL 
                ELSE 
                    ROUND(account_move.exchange_rate, 3) 
            END AS exchange_rate,
            LEFT(COALESCE(TO_CHAR(account_move.origin_invoice_date, 'DD/MM/YYYY'), ''), 10) AS origin_invoice_date,
            LEFT(COALESCE(origin_document_type.code, ''), 2) AS origin_document_type_code,
            LEFT(COALESCE(SPLIT_PART(REPLACE(account_move.origin_number, ' ', ''), '-', 1), ''), 20) AS origin_number_serie,
            CASE 
                WHEN account_move.move_type = 'in_refund' THEN 
                    LEFT(COALESCE(code_aduana.code, ''), 3) 
                ELSE 
                    '' 
            END AS code_aduana,
            LEFT(COALESCE(SPLIT_PART(REPLACE(account_move.origin_number, ' ', ''), '-', 2), ''), 20) AS origin_number_correlative,
            LEFT(COALESCE(classification_services.code, ''), 1) AS classification_services_code,
            CASE 
                WHEN account_move.detraction_id IS NOT NULL THEN 
                    'TieneDetraccion' 
                ELSE 
                    '' 
            END AS detraction,
            LEFT(COALESCE(inv_type_document.code, ''), 2) AS inv_type_document_code,
            COALESCE(country.name) AS country_name,
            COALESCE(partner.street, '') AS partner_street
        """

    def _from_sire_purchase(self):
        return """
            account_move                             AS account_move
            INNER JOIN res_partner                   AS partner                  ON account_move.partner_id = partner.id
            INNER JOIN res_company                   AS company                  ON account_move.company_id = company.id
            INNER JOIN res_currency                  AS currency                 ON account_move.currency_id = currency.id
            LEFT JOIN l10n_latam_document_type       AS origin_document_type     ON account_move.origin_l10n_latam_document_type_id = origin_document_type.id
            LEFT JOIN l10n_latam_document_type       AS document_type            ON account_move.l10n_latam_document_type_id = document_type.id
            LEFT JOIN l10n_latam_identification_type AS identification_type      ON partner.l10n_latam_identification_type_id = identification_type.id
            LEFT JOIN res_country                    AS country                  ON partner.country_id = country.id
            LEFT JOIN link_economic                  AS link_economic            ON account_move.linkage_id = link_economic.id
            LEFT JOIN exoneration_nodomicilied       AS exoneration_nodomicilied ON account_move.exoneration_nodomicilied_id = exoneration_nodomicilied.id
            LEFT JOIN type_rent                      AS type_rent                ON account_move.type_rent_id = type_rent.id
            LEFT JOIN service_taken                  AS service_taken            ON account_move.taken_id = service_taken.id
            LEFT JOIN code_aduana                    AS code_aduana              ON account_move.code_aduana = code_aduana.id
            LEFT JOIN l10n_latam_document_type       AS inv_type_document        ON account_move.inv_type_document = inv_type_document.id
            LEFT JOIN classification_services        AS classification_services  ON account_move.types_goods_services_id = classification_services.id
        """

    def _where_sire_purchase(self):
        return f"""
            (
                (
                    account_move.company_id = {self.company_id.id}
                    AND account_move.move_type IN ('in_invoice', 'in_refund')
                )
                AND (
                    DATE_PART('year', account_move.ple_date) = {self.year}
                    AND DATE_PART('month', account_move.ple_date) = {self.month}
                )
                AND (
                    account_move.state NOT IN ('draft', 'cancel')
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
                            journal.type = 'purchase'
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

    def _group_by_sire_purchase(self):
        return ""

    def _order_by_sire_purchase(self):
        return """
            account_move.date DESC,
            account_move.name DESC,
            account_move.id DESC
        """

    def _query_sire_purchase(self):
        group_by_ = self._group_by_sire_purchase()
        return f"""
            SELECT {self._select_sire_purchase()}
            FROM {self._from_sire_purchase()}
            WHERE {self._where_sire_purchase()}
            {"GROUP BY" + group_by_ if group_by_ else ""}
            ORDER BY {self._order_by_sire_purchase()}
        """

    def _execute_query_sire_purchase(self):
        try:
            self.env.cr.execute(self._query_sire_purchase())
            return self.env.cr.dictfetchall()
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la consulta, contacte al administrador: \n {error}')

    def _process_query_results(self):
        query_results = self._execute_query_sire_purchase()
        for line_result in query_results:
            country_name = line_result.get('country_name')
            if isinstance(country_name, dict):
                last_key = list(country_name.keys())[-1]
                new_country_name = country_name[last_key]
            else:
                new_country_name = country_name or ''
            tax_data = ast.literal_eval(line_result['tax_data'])
            line_result.update({
                'p_base_gdg': tax_data[0],
                'p_tax_gdg': tax_data[1],
                'p_base_gdm': tax_data[2],
                'p_tax_gdm': tax_data[3],
                'p_base_gdng': tax_data[4],
                'p_tax_gdng': tax_data[5],
                'p_base_ng': tax_data[6],
                'p_tax_isc': tax_data[7],
                'p_tax_icbp': tax_data[8],
                'p_tax_other': tax_data[9],
                'amount_total': tax_data[10] if len(tax_data) == 11 else sum(tax_data[:10]) * -1,
                'hard_rent': self._get_values_error(line_result.get('hard_rent', '')),
                'deduccion_cost': self._get_values_error(line_result.get('deduccion_cost', '')),
                'neto_rent': self._get_values_error(line_result.get('neto_rent', '')),
                'retention_rate': self._get_values_error(line_result.get('retention_rate', '')),
                'tax_withheld': self._get_values_error(line_result.get('tax_withheld', '')),
                'country_name': new_country_name,
            })
        return query_results

    def _get_values_error(self, value):
        data = value.strip()
        return '0.00' if data == '.00' else data
