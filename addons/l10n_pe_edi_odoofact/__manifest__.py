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
    "name": "Facturacion Electronica",
    "version": "16.0.1.0.7",
    "author": "OPeru",
    "category": "Accounting & Finance",
    "summary": "Modulo para Facturacion Electronica.",
    "license": "LGPL-3",
    "contributors": [
        "Soporte OPeru <soporte@operu.pe>",
    ],
    "website": "http://www.operu.pe/facturacion-electronica",
    "depends": [
        "l10n_pe",
        "l10n_pe_edi_base",
        "l10n_latam_invoice_document",
        "account_debit_note",
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/account_tax_data.xml",
        "data/l10n_latam_identification_type_data.xml",
        "data/l10n_latam_document_type_data.xml",
        "data/mail_template_data.xml",
        "wizards/account_move_reversal_views.xml",
        "wizards/account_debit_note_views.xml",
        "wizards/l10n_pe_edi_move_cancel_views.xml",
        "views/account_journal_views.xml",
        "views/product_template_views.xml",
        "views/account_move_views.xml",
        "views/report_invoice.xml",
        "views/res_config_settings_views.xml",
    ],
    "external_dependencies": {
        "python": [
            "num2words",
        ],
    },
    "installable": True,
    "images": ["static/description/banner.png"],
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}
