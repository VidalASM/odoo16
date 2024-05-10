from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PleCashBank(models.Model):
    _inherit = 'ple.report.cash.bank'

    def action_generate_excel(self):
        query_cash = """
            SELECT
            coalesce(TO_CHAR(account_move_line.date, 'YYYYMM00'), '') as period,
            replace(replace(replace(account_move_line__move_id.name, '/', ''), '-', ''), ' ', '') as cuo,
            (SELECT
                CASE
                    WHEN company.ple_type_contributor = 'CUO' THEN
                        (SELECT COALESCE(ple_correlative, 'M000000001') FROM account_move_line WHERE move_id = account_move_line__move_id.id  LIMIT 1)
                    WHEN company.ple_type_contributor = 'RER' THEN 'M-RER'
                    ELSE ''
                END
            ) as correlative,
            coalesce(trim(replace(replace(replace(account_account.code, '/', ''), '-', ''), '.', '')), '') as account_code,
            get_unit_operation_code(account_move_line__move_id.id) as unit_operation_code,
            '' as cost_center_code,
            coalesce(currency.name, 'PEN') as currency_name,
            (SELECT 
                CASE
                    WHEN account_move_line.serie_correlative IS NOT NULL THEN
                        SUBSTRING(split_part(replace(account_move_line.serie_correlative, ' ', ''), '-',1),1,4)
                    ELSE '0000'
                END
            ) as serie,
            (SELECT 
                CASE
                    WHEN account_move_line.serie_correlative IS NOT NULL THEN
                        SUBSTRING(split_part(replace(account_move_line.serie_correlative, ' ', ''), '-', 2),1,8)
                    ELSE '00000000'
                END
            ) as document_number,
            coalesce(document_type.code, '00') AS type_payment_document,
            coalesce(TO_CHAR(account_move_line__move_id.date, 'DD/MM/YYYY'), '') as accounting_date,
            coalesce(TO_CHAR(account_move_line__move_id.invoice_date_due, 'DD/MM/YYYY'), '') as date_due,
            coalesce(TO_CHAR(account_move_line__move_id.date, 'DD/MM/YYYY'), '') as operation_date,
            (CASE WHEN account_move_line__move_id.ref IS NOT NULL THEN
                account_move_line__move_id.ref ELSE
                    SUBSTRING(account_move_line.name,1 ,200) END) as gloss,
            coalesce(account_move_line.name, '') as referential_gloss,
            UDF_numeric_char(account_move_line.debit) as debit, 
            UDF_numeric_char(account_move_line.credit) as credit,
            account_move_line.serie_correlative as id_group_sc,
            account_move_line.id as id_aml,
            data_structured_cash(account_move_line.serie_correlative) as data_structured_cash,
            account_move_line.full_reconcile_id as full_reconcile_id,
            account_move_line.ple_correlative as ple_correlative,
            account_move_line__move_id.name as am_name,
            TO_CHAR(account_move_line__move_id.date, 'YYYYMM00') as am_date,
            res_partner.country_id as country_partner,
            part.country_id as country_comp_partner, 
            account_journal.type as aj_type
            -- QUERIES TO MATCH MULTI TABLES
            FROM "account_move" as "account_move_line__move_id","account_move_line"
            --  https://www.sqlshack.com/sql-multiple-joins-for-beginners-with-examples/
            --  TYPE JOIN |  TABLE                         | VARIABLE                    | MATCH
                LEFT JOIN   "account_account"                account_account       ON  account_move_line.account_id = account_account.id
                INNER JOIN  "res_currency"                   currency              ON  account_move_line.currency_id = currency.id
                INNER JOIN	"res_company"					 company			   ON  account_move_line.company_id = company.id
                LEFT JOIN   "l10n_latam_document_type"       document_type         ON  account_move_line.l10n_latam_document_type_id = document_type.id
                LEFT JOIN   res_partner                                            ON  account_move_line.partner_id = res_partner.id
                LEFT JOIN   account_journal                                        ON  account_move_line.journal_id = account_journal.id 
                LEFT JOIN   res_company                                            ON  account_move_line.company_id = res_company.id
                LEFT JOIN   res_partner as part                                    ON  res_company.partner_id = part.id
            WHERE
            -- FILTER QUERIES
            ("account_move_line"."move_id"="account_move_line__move_id"."id") AND
                    ((((("account_move_line"."account_id" in (SELECT "account_account".id
                    FROM "account_account" WHERE "account_account"."ple_selection" = '{ple_selection}'
                    AND ("account_account"."company_id" IS NULL OR
                    ("account_account"."company_id" in ({company_id})))
                    ORDER BY "account_account"."id"))  AND
                    ("account_move_line"."date" >= '{date_start}'))  AND
                    ("account_move_line"."date" <= '{date_end}'))  AND
                    ("account_move_line"."company_id" = {company_id}))  AND
                    ("account_move_line__move_id"."state" = '{state}')) AND
                    ("account_move_line"."company_id" IS NULL   OR  ("account_move_line"."company_id" in ({company_id})))
            -- ORDER DATA
            ORDER BY "account_move_line"."date" DESC,"account_move_line"."move_name" DESC,"account_move_line"."id"
                """.format(
            ple_selection='cash',
            company_id=self.company_id.id,
            date_start=self.date_start,
            date_end=self.date_end,
            state='posted',
            ple_report_cash_bank=self.id
        )

        query_bank = """
            SELECT
            coalesce(TO_CHAR(account_move_line.date, 'YYYYMM00'), '') as period,
            replace(replace(replace(account_move_line__move_id.name, '/', ''), '-', ''), ' ', '') as cuo,
            (SELECT
                CASE
                    WHEN company.ple_type_contributor = 'CUO' THEN
                        (SELECT COALESCE(ple_correlative, 'M000000001') FROM account_move_line WHERE move_id = account_move_line__move_id.id  LIMIT 1)
                    WHEN company.ple_type_contributor = 'RER' THEN 'M-RER'
                    ELSE ''
                END
            ) as correlative,
            coalesce(res_bank.sunat_bank_code, '') as bank_code,
            coalesce(res_partner_bank.acc_number, '') as account_bank_code,
            TO_CHAR(account_move_line.date, 'DD/MM/YYYY') as date,
            coalesce(account_move_line.name, '-') as operation_description,
            coalesce(payment_methods.code, '003') as payment_method,
            coalesce(identification_type.l10n_pe_vat_code, '-') as partner_type_document,
            coalesce(partner.vat, '-') as partner_document_number,
            coalesce(partner.name, 'VARIOS') as partner_name,
            (SELECT
                CASE
                    WHEN account_bankSL.transaction_type IS NOT NULL THEN
                        validate_string(account_bankSL.transaction_type, 20)
                    WHEN account_move_line__move_id.ref is not NULL THEN
                        validate_string(account_move_line__move_id.ref, 20)
                    WHEN account_move_line__move_id.name is not NULL THEN
                        validate_string(account_move_line__move_id.name, 20)
                    ELSE ''
                END
            ) as transaction_number,
            --trim(LEADING ' ' TO_CHAR(account_move_line.debit, '9999999.99')) as debit, 
            --TO_CHAR(account_move_line.debit, '0.99') as debit, 
            UDF_numeric_char(account_move_line.debit) as debit,     
            UDF_numeric_char(account_move_line.credit) as credit
            -- QUERIES TO MATCH MULTI TABLES
            FROM "account_move" as "account_move_line__move_id","account_move_line"
            --  https://www.sqlshack.com/sql-multiple-joins-for-beginners-with-examples/
            --  TYPE JOIN |  TABLE                         | VARIABLE                    | MATCH
                LEFT JOIN   "res_partner"                    partner               ON  account_move_line.partner_id = partner.id
                LEFT JOIN   "account_account"                account_account       ON  account_move_line.account_id = account_account.id
                INNER JOIN  "res_currency"                   currency              ON  account_move_line.currency_id = currency.id
                INNER JOIN	"res_company"					 company			   ON  account_move_line.company_id = company.id
                LEFT JOIN   "account_bank_statement_line"    account_bankSL        ON  account_move_line.statement_line_id = account_bankSL.id
                LEFT JOIN   "payment_methods_codes"          payment_methods       ON  account_bankSL.means_payment_id = payment_methods.id
                LEFT JOIN   "res_partner_bank"               res_partner_bank      ON  account_account.bank_id = res_partner_bank.id
                LEFT JOIN   "res_bank"                       res_bank              ON  res_partner_bank.bank_id = res_bank.id
                LEFT JOIN   "l10n_latam_identification_type" identification_type   ON  partner.l10n_latam_identification_type_id = identification_type.id
            WHERE
            -- FILTER QUERIES
            ("account_move_line"."move_id"="account_move_line__move_id"."id") AND
                    ((((("account_move_line"."account_id" in (SELECT "account_account".id
                    FROM "account_account" WHERE "account_account"."ple_selection" = '{ple_selection}'
                    AND ("account_account"."company_id" IS NULL OR
                    ("account_account"."company_id" in ({company_id})))
                    ORDER BY "account_account"."id"))  AND
                    ("account_move_line"."date" >= '{date_start}'))  AND
                    ("account_move_line"."date" <= '{date_end}'))  AND
                    ("account_move_line"."company_id" = {company_id}))  AND
                    ("account_move_line__move_id"."state" = '{state}')) AND
                    ("account_move_line"."company_id" IS NULL   OR  ("account_move_line"."company_id" in ({company_id})))
            -- ORDER DATA
            ORDER BY "account_move_line"."date" DESC,"account_move_line"."move_name" DESC,"account_move_line"."id"
                """.format(
            ple_selection='bank',
            company_id=self.company_id.id,
            date_start=self.date_start,
            date_end=self.date_end,
            state='posted',
            ple_report_cash_bank=self.id
        )

        try:
            self.env.cr.execute(query_cash)
            data_cash = self.env.cr.dictfetchall()
            self.env.cr.execute(query_bank)
            data_bank = self.env.cr.dictfetchall()
            self.get_excel_data(data_cash, data_bank)
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la query, comunicarse con el administrador: \n {error}')