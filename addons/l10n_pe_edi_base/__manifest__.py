#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

{
    "name": "E-Documents",
    "version": "16.0.1.1.0",
    "author": "OPeru",
    "category": "Accounting & Finance",
    "summary": "Módulo base para Documentos Electrónicos.",
    "license": "LGPL-3",
    "contributors": [
        "Soporte OPeru <soporte@operu.pe>",
    ],
    "website": "http://www.operu.pe/facturacion-electronica",
    "depends": [
        "l10n_pe_edi_catalog",
        "mail",
        "uom",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/ir_cron_data.xml",
        "data/l10n_pe_edi_supplier_data.xml",
        "data/l10n_pe_edi_document_type_data.xml",
        "data/uom_uom_data.xml",
        "views/edi_shop_views.xml",
        "views/edi_request_document_type_views.xml",
        "views/edi_request_views.xml",
        "views/res_config_settings_views.xml",
        "views/uom_uom_views.xml",
        "views/l10n_pe_edi_base_menuitem.xml",
    ],
    "assets": {
        "web.report_assets_common": ["l10n_pe_edi_base/static/src/scss/style.scss"]
    },
    "external_dependencies": {
        "python": [
            "python-dateutil",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 1,
    "post_init_hook": "post_init_hook",
}
