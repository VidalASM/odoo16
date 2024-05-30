#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from os.path import dirname, join, realpath

from odoo import SUPERUSER_ID, api


def _load_catalog_03_data(cr, registry):
    csv_path = join(
        dirname(realpath(__file__)),
        "data",
        "l10n_pe_edi.catalog.03.csv",
    )
    csv_file = open(csv_path, "rb")
    # Reading the header
    csv_file.readline()
    cr.copy_expert(
        """
        COPY l10n_pe_edi_catalog_03 (code, name, active)
        FROM STDIN WITH DELIMITER '|'
        """,
        csv_file,
    )
    # Creating xml_ids
    cr.execute(
        """
        INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
        SELECT concat('l10n_pe_edi_cat03_', code), id, 'l10n_pe_edi_catalog',
            'l10n_pe_edi.catalog.03', 't'
        FROM l10n_pe_edi_catalog_03
        """
    )


def _compute_catalog_03_complete_name(env):
    records = env["l10n_pe_edi.catalog.03"].search([])
    records._compute_complete_name()


def _load_catalog_25_data(cr, registry):
    csv_path = join(
        dirname(realpath(__file__)),
        "data",
        "l10n_pe_edi.catalog.25.csv",
    )
    csv_file = open(csv_path, "rb")
    # Reading the header
    csv_file.readline()
    cr.copy_expert(
        """
        COPY l10n_pe_edi_catalog_25 (code, name, active)
        FROM STDIN WITH DELIMITER '|'
        """,
        csv_file,
    )
    # Creating xml_ids
    cr.execute(
        """
        INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
        SELECT concat('l10n_pe_edi_cat25_', code), id, 'l10n_pe_edi_catalog',
            'l10n_pe_edi.catalog.25', 't'
        FROM l10n_pe_edi_catalog_25
        """
    )


def _compute_catalog_25_complete_name(env):
    records = env["l10n_pe_edi.catalog.25"].search([])
    records._compute_complete_name()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _load_catalog_03_data(cr, registry)
    _compute_catalog_03_complete_name(env)
    _load_catalog_25_data(cr, registry)
    _compute_catalog_25_complete_name(env)


def uninstall_hook(cr, registry):
    cr.execute("DELETE FROM l10n_pe_edi_catalog_03;")
    cr.execute("DELETE FROM ir_model_data WHERE model='l10n_pe_edi.catalog.03';")
    cr.execute("DELETE FROM l10n_pe_edi_catalog_25;")
    cr.execute("DELETE FROM ir_model_data WHERE model='l10n_pe_edi.catalog.25';")
