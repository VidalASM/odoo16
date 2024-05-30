{
    'name': 'Cambiar cuenta corriente facturas',
    'version': '16.0.0.1.4',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'The account receivable and payable of the invoices, changes according to the currency and the type of proof of payment.',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 8.00,
    'category': 'Accounting/Accounting',
}
