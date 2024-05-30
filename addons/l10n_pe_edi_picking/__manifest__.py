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
    'name': 'Guias electronicas Peru - PSE/OSE Nubefact',
    'version': '15.0.7',
    'author': 'OPeru',
    'category': 'Accounting',
    'summary': 'Electronic Picking Peru - PSE/OSE Nubefact',
    'description': '''
    EDI Peruvian Localization
    Electronic Picking Peru - PSE/OSE Nubefact

    ''',
    'website': 'hhttp://www.operu.pe/facturacion-electronica',
    'depends': [
        'base', 
        'stock', 
        'l10n_pe_edi_odoofact',
    ],
    'data': [
        'data/ir_sequence.xml',
        'data/cron_stock_picking.xml',
        'wizards/masive_picking_sending_view.xml',
        'views/res_config_settings_views.xml',
        'views/stock_picking_view.xml',
        'views/l10n_pe_edi_picking_number_view.xml',
        'report/epicking_report_template.xml',
        'report/epicking_report.xml',
        'security/ir.model.access.csv', 
    ],
    'installable': True,
    'images': ['static/description/banner.png'],
    'live_test_url': 'http://operu.pe/manuales',
    'license': 'OPL-1',
    'price': 99.00,
    'currency': 'USD',
    'sequence': 1,
    'support': 'modulos@operu.pe',
}
