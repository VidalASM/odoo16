{
    'name': 'Field for carrier reference number on the invoice',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': '''
    Add a Field in the invoice to place the reference number related to the invoice.
    ''',
    'Description': '''
    Add a Field in the invoice to place the reference number related to the invoice.
    ''',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'views/account_move.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
