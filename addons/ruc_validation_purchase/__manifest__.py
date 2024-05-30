{
    'name': 'Ruc Validation desde Compras',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'It allows you to control whether a RUC is Active or Ingrained at the time of placing a purchase order.',
    'category': 'Accounting',
    'depends': [
        'purchase',
        'ruc_validation_sunat'
    ],
    'data': ['views/purchase_views.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 10.00
}
