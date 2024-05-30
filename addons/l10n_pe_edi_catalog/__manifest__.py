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
    "name": "Catalogos SUNAT",
    "version": "16.0.1.0.1",
    "author": "OPeru",
    "category": "Accounting & Finance",
    "summary": "Datos de Tablas para la factura electronica.",
    "license": "LGPL-3",
    "contributors": [
        "Soporte OPeru <soporte@operu.pe>",
    ],
    "website": "http://www.operu.pe/facturacion-electronica",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/catalog_data.xml",
        "data/ple_table_data.xml",
        "views/catalog_views.xml",
        "views/table_views.xml",
    ],
    "installable": True,
    "images": ["static/description/banner.png"],
    "auto_install": False,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
