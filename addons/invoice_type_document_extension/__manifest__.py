{
    "name": "Related fields for purchases and sales",
    "version": "16.0.0.0.1",
    "author": "Ganemo",
    "website": "https://www.ganemo.co",
    "live_test_url": "https://www.ganemo.co",
    "summary": "This module will allow us to place the type of document, document series and payment voucher number automatically through the records of purchase and sale invoices.",
    "description": """This module will allow us to place the type of document, document series and payment voucher number automatically through the records of purchase and sale invoices.""",
    "category": "Accounting",
    "depends": ['invoice_type_document', 'stock', 'l10n_pe_delivery_note_ple'],
    'data': [
        'views/stock_picking_views.xml'
    ],
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 0.00,
}
