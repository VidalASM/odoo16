{
    'name': 'Register of Cash and banks PLE - SUNAT (Perú) - Enterprise',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co/ple',
    'summary': 'Register of Cash and banks PLE - SUNAT (Perú) - Enterprise',
    'description': """
    Generates the electronic register of Cash and Banks in .txt file, ready to present to SUNAT via electronic book program (PLE - SUNAT).
    This is a mandatory e-book for companies that are required to keep complete accounting.
    """,
    'category': 'Accounting',
    'depends': ['ple_cash_book', 'account_accountant'],
    'data': ['views/account_views.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 160.00
}
