{
    'name': 'Field for aditional document reference on the invoice',
    'version': '16.0.0.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'We are going to add some new fields in the invoice (account.move) so that it is later sent in XML tags.',
    'description': "We are going to add some new fields in the invoice (account.move) so that it is later sent in XML tags.",
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'views/move_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
