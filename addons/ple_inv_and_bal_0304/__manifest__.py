{
    'name': 'Formato 3.4 Libro de Inventarios y Balances - Cuentas por Cobrar al Personal: Trab. Soc. Acc. Ger. Direc.',
    'version': '16.0.0.0.6',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'summary': 'This module creates the format 3.4 "Accounts receivable from workers" of the electronic inventory and balance book.',
    'description': """
This module creates the format 3.4 "Accounts receivable from workers" of the electronic inventory and balance book.""",
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'financial_statement_annexes',
        'ple_inv_and_bal_0302',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/ple_inv_bal_views_02_inherit.xml',
        'reports/ple_inv_bal_04_report.xml',
        'reports/ple_inv_bal_04_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 25.00
}
