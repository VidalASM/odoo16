from . import models
from odoo import api, SUPERUSER_ID


def _update_data_trial_balances(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    trial_balances_catalog = env['trial.balances.catalog'].search([])
    account_code_999999 = env['account.account'].search([('code', '=', '999999')])
    for rec in trial_balances_catalog:
        code = rec.code
        try:
            account_code_999999.trial_balances_catalog_id = rec.id if rec.code == '89' else False
            account_account_base = env.ref('l10n_pe.1_chart%s' % code)
            account_account_base.trial_balances_catalog_id = rec.id
        except:
            pass