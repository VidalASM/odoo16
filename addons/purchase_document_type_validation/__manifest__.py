{
    'name': 'Purchase document type validation',
    'version': '16.0.0.0.4',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': "This module allows you to configure the Validation of identification documents parameters.",
    'category': 'Accounting',
    'depends': ['l10n_latam_invoice_document'],
    'data': [
          'views/account_move_views.xml'
    ],
    "assets": {
            "web.assets_backend": [
                "purchase_document_type_validation/static/src/css/classes.css",
            ],
        },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
