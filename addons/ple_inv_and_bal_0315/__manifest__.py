{
    'name': 'Formato 3.15 Libro de Inventarios y Balances - Activos y pasivos Diferidos',
    'version': '16.0.0.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module creates the format 3.15 "Deferred assets and liabilities" of the electronic inventory and balance book.',
    'description': 'This module creates the format 3.15 "Deferred assets and liabilities" of the electronic inventory and balance book.',
    'live_test_url': 'https://www.ganemo.co/demo',
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'financial_statement_annexes',
        'ple_inv_and_bal_0302',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ple_inv_bal_15_views.xml',
        'reports/ple_inv_bal_report.xml',
        'reports/ple_inv_bal_template.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'ple_inv_and_bal_0315/static/src/css/main.css',
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 25.00
}
