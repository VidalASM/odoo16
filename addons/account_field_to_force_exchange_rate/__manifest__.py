{
    'name': 'Account field to force exchange rate',
    'version': '16.0.2.0.5',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module will create a field to force the exchange rate',
    'category': 'Accounting',
    'depends': ['account_exchange_currency'],
    'data': [
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 100.00
}
