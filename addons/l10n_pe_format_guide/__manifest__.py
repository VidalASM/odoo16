{
    "name": "l10npe_formatguide",
    "version": "16.0.0.0.2",
    "author": "Ganemo",
    "live_test_url": "https://www.ganemo.co/demo",
    "website": "https://www.ganemo.co",
    "category": "Accounting",
    "description": "The object is to create a predefined format so that you can print under an already established template.",
    "summary": "The object is to create a predefined format so that you can print under an already established template.",
    "depends": ['account', 'base', 'l10n_pe_edi_stock', 'l10n_latam_base', 'invoice_type_document_extension', 'l10n_pe_delivery_note_20_extension'],
    'data': [
        'views/res_partner_view.xml',
        'views/product_template_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_picking_report.xml',
        'views/report_guide.xml',
    ],
    "license": "Other proprietary",
    "currency": "USD",
    "price": 00.00,
    'installable': True,
    "auto_install": False,

}
