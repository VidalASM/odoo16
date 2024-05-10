{
    "name": "Invoice Validation by Document",
    "version": "16.0.0.3.0",
    "author": "Ganemo",
    "website": "https://www.ganemo.co",
    "live_test_url": "https://www.ganemo.co",
    "summary": "This module will allow you to select and restrict the type of document and the payment receipts that the country has.",
    'description': """
    This module will allow you to select and restrict the type of document and the payment receipts that the country has.
    """,
    "category": "Accounting",
    "depends": ["document_type_validation",
                "l10n_latam_invoice_document",
                "contacts"
                ],
    'data': [
        'views/invoice_validation_document.xml'
    ],
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 50.00,
}