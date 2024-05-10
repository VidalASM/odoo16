from . import models

def post_init_hook(cr,registry):
    sql_query = """ALTER TABLE res_currency_rate DROP CONSTRAINT IF EXISTS res_currency_rate_unique_name_per_day;"""
    cr.execute(sql_query)

def uninstall_hook(cr, registry):
    sql_query = """ALTER TABLE res_currency_rate ADD CONSTRAINT res_currency_rate_unique_name_per_day unique (name,currency_id,company_id);"""
    cr.execute(sql_query)