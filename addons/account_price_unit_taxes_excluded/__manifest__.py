{
    'name': 'Price unit taxes excluded',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': '''
       This módule will create a field called “unite value” that will be excluded from taxes.
    ''',
    'category': 'Accounting',
    'depends': [
        'account',
        'sale',
        'purchase',
    ],
     'data': [
        'views/account_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 25.00
}
