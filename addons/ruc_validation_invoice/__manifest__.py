{
    'name': 'Ruc Validation desde Facturas',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'It allows you to control whether a RUC is Active or Ingrained at the time of making a purchase invoice.',
    'category': 'Accounting',
    'depends': [
        'ruc_validation_sunat',
        'purchase_document_type_validation'
    ],
    'data': [
        'views/account_views.xml',
        'views/l10n_latam_document_type_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 10.00
}
