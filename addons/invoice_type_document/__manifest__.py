{
    "name": "Place invoice data in reconciliations",
    "version": "16.0.0.1.4",
    "author": "Ganemo",
    "website": "https://www.ganemo.co",
    "live_test_url": "https://www.ganemo.co",
    "summary": "This module will allow us to place the type of document, document series and payment receipt number automatically through the reconciliations.",
    "description": """
        This module will allow us to place the type of document, 
        document series and payment receipt number automatically 
        through the reconciliations.
    """,
    "category": "Accounting",
    "depends": ['account', 
                'l10n_latam_invoice_document'],
    'data': [
        'views/account_views.xml'
    ],
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 25.00,
}
