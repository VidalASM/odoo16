{
    'name': 'Formato 3.5 Libro de Inventarios y Balances - Cuentas por Cobrar Diversas - Terc y Relac.',
    'version': '16.0.0.0.5',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module creates the format 3.5 "various accounts receivable" of the electronic inventory and balance book',
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'financial_statement_annexes',
        'ple_inv_and_bal_0302',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/ple_inv_bal_views_02_inherit.xml',
        'reports/ple_inv_bal_05_report.xml',
        'reports/ple_inv_bal_05_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 25.00
}
