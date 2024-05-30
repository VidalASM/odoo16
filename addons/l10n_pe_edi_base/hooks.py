#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from odoo import SUPERUSER_ID, _, api


def _create_shop(env):
    """This hook is used to add a shop on existing companies
    when module l10n_pe_edi_odoofact is installed.
    """
    company_ids = (
        env["res.company"].search([]).filtered(lambda r: r.country_id.code == "PE")
    )
    company_with_shop = env["l10n_pe_edi.shop"].search([]).mapped("company_id")
    company_without_shop = company_ids - company_with_shop
    for company in company_without_shop:
        env["l10n_pe_edi.shop"].create(
            {
                "name": "%s (%s)" % (company.name, _("Shop")),
                "code": "0000",
                "company_id": company.id,
                "partner_id": company.partner_id.id,
            }
        )


def _change_values_paperformat_a4(env):
    paperformat_id = env.ref("base.paperformat_euro", False)
    if paperformat_id:
        paperformat_id.write(
            {
                "margin_top": 30,
                "margin_bottom": 20,
                "header_spacing": 25,
            }
        )


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _create_shop(env)
    _change_values_paperformat_a4(env)
