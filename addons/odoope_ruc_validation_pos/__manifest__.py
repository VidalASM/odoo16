# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

{
    'name' : 'Validador RUC para punto de venta',
    'version' : '14.0.1',
    'author' : 'OPeru',
    'category' : 'Generic Modules/Base',
    'summary': 'Validator RUC for Point of Sale',
    'description': ''' Validator RUC , Point of Sale.''',
    'depends' : ['l10n_pe_vat_sunat',
                 'l10n_pe_edi_pos'
                ],
    'qweb': [
        # 'static/src/xml/*.xml'
    ],            
    'data': [
        # 'views/pos_import.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'images': ['static/description/banner.png'],
    "assets": {
        "point_of_sale.assets": [
            # "odoope_ruc_validation_pos/static/src/js/Client/models.js",
            "odoope_ruc_validation_pos/static/src/js/Client/ClientDetailsEdit.js",
            # "odoope_ruc_validation_pos/static/src/js/Client/ClientListScreen.js",
            # "odoope_ruc_validation_pos/static/src/xml/pos.xml",
        ],
    },
    'live_test_url': 'http://operu.pe/manuales',
    'license': 'OPL-1',
    'price': 19.00,
    'currency': 'USD',
    'sequence': 1,
    'support': 'modulos@operu.pe',
}