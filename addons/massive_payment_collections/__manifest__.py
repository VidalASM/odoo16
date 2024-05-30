{
    "name": "Registro de pagos y cobros desde apuntes contables",
    "version": "16.0.3.0.3",
    "author": "Ganemo",
    "website": "https://www.ganemo.co",
    "live_test_url": "https://www.ganemo.co",
    "summary": "This module will be used to make massive collections and payments from the accounting notes, it will create the accounting entries in the payments of suppliers and clients.",
    'description': """
        This module will be used to make massive collections and payments from the accounting notes, 
        it will create the accounting entries in the payments of suppliers and clients.
    """,
    "category": "Accounting",
    "depends": ["account", "account_field_to_force_exchange_rate"],
    'data': [
        'security/ir.model.access.csv',
        'wizard/massive_payment_collections_views.xml'
    ],
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 50.00,
}
