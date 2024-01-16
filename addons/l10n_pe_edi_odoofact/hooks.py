#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from odoo import SUPERUSER_ID, api


def _change_identification_type_ruc(env):
    vat_id = env.ref("l10n_latam_base.it_vat")
    ruc_id = env.ref("l10n_pe.it_RUC")
    if vat_id and ruc_id:
        partner_ids = env["res.partner"].search(
            [
                ("l10n_latam_identification_type_id", "=", vat_id.id),
                ("country_code", "=", "PE"),
                ("vat", "not in", [False, ""]),
            ]
        )
        if partner_ids:
            partner_ids = partner_ids.filtered(
                lambda x: len(x.vat) == 11 and str(x.vat).isnumeric()
            )
            partner_ids.write({"l10n_latam_identification_type_id": ruc_id.id})


def _change_fiscal_position_exp(env):
    company_ids = (
        env["res.company"].search([]).filtered(lambda r: r.country_id.code == "PE")
    )
    for company_id in company_ids:
        fiscal_pos_exp = env["account.fiscal.position"].search(
            [("name", "ilike", "expor"), ("company_id", "=", company_id.id)], limit=1
        )
        tax_unaffected = env["account.tax"].search(
            [
                ("type_tax_use", "=", "sale"),
                ("l10n_pe_edi_tax_code", "=", "9998"),
                ("company_id", "=", company_id.id),
            ],
            limit=1,
        )
        if fiscal_pos_exp and tax_unaffected:
            for tax_id in fiscal_pos_exp.tax_ids:
                if tax_id.tax_src_id.tax_group_id.name == "IGV":
                    tax_id.tax_dest_id = tax_unaffected.id


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _change_identification_type_ruc(env)
    _change_fiscal_position_exp(env)
