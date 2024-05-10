{
    'name': 'Payment term lines',
    'version': '16.0.2.3.6',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module will create a field to force the exchange rate',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'views/payment_line_view.xml',
        'views/account_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 100.00
}
