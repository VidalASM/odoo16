from odoo import api, models

class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    @api.constrains('name', 'currency_id', 'company_id')
    def _constraint_currency_rate_unique_name_per_day(self):
        return
    @api.model
    def _verifcate_contrainst(self):
        sql_verification = """
                       SELECT
                           indexname

                       FROM
                           pg_indexes
                       WHERE
                           tablename = 'res_currency_rate' AND  indexname = 'res_currency_rate_unique_name_per_day';
               """
        self.env.cr.execute(sql_verification)

        restriction = self.env.cr.fetchall()

        if len(restriction) > 0:
            sql_query = """ALTER TABLE res_currency_rate DROP CONSTRAINT IF EXISTS res_currency_rate_unique_name_per_day;"""
            self.env.cr.execute(sql_query)