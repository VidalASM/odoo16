# -*- coding: utf-8 -*-
{
    'name': 'EDI for Peru with PSE',
    'version': '1.0',
    'summary': 'Electronic Invoicing for Peru using direct connection with PSE',
    'category': 'Accounting/Localizations/EDI',
    'author': 'Obox',
    'license': 'OPL-1',
'description': """
Extends EDI Peru Localization
=============================
- Working with a Authorized Supplier for electronic invoices
- Manage the following electronic documents: Factura, Boleta, Nota de Credito, Nota de Debito, Factura + Percepción
- Support Cancellation of any documents
- Support Credit notes with foreign references
- Support Credit note with payment fee definition
- Support Down Payments integrated with sales and foreign references
- Support Invoices with customer withholdings (Only customers authorized as agent by SUNAT)
- Support Invoices with transport references
    """,
    'depends': [
        'l10n_pe_edi',
    ],
    "data": [
        'data/account_edi_data.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/res_partner_view.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
}