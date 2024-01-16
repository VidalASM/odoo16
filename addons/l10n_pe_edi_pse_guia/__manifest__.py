# -*- coding: utf-8 -*-
{
    'name': 'Peruvian - Electronic Delivery Note with PSE',
    'version': '1.0',
    'summary': 'Electronic Delivery Note for Peru (REST API with PSE)',
    'category': 'Accounting/Localizations/EDI',
    'author': 'Obox',
    'license': 'OPL-1',
'description': """
Extends Electronica Delivery Note
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
        'l10n_pe_edi_pse_factura',
        'l10n_pe_edi_stock',
    ],
    "data": [
        'views/res_partner_view.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
}