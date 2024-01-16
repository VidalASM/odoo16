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
    "name": "Validador de Datos - Peru",
    "version": "16.0.1.0.0",
    "author": "OPeru",
    "category": "Generic Modules/Base",
    "summary": "RUC validator - PERU",
    "license": "LGPL-3",
    "contributors": [
        "Soporte OPeru <soporte@operu.pe>",
    ],
    "website": "http://www.operu.pe/facturacion-electronica",
    "depends": ["web", "iap", "l10n_latam_base", "l10n_pe", "l10n_pe_edi_base"],
    "data": [
        "views/res_partner_view.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/validation_info_templates.xml",
    ],
    "qweb": [],
    "demo": [],
    "test": [],
    "images": [
        "static/description/banner.png",
    ],
    "support": "modulos@operu.pe",
    "installable": True,
    "auto_install": False,
    "sequence": 1,
    "post_init_hook": "_odoope_ruc_validation_init",
}
