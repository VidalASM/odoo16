{
    'name': 'Formato 3.13 Libro de Inventarios y Balances - Cuentas por Pagar diversas de Terceros y Relacionadas',
    'version': '16.0.0.0.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'summary': 'This module creates the format 3.13 "Related Accounts Payable" of the electronic inventory and balance book.',
    'description': 'This module creates the format 3.13 "Related Accounts Payable" of the electronic inventory and balance book.',
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'financial_statement_annexes',
        'ple_inv_and_bal_0302',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ple_inv_bal_13_views.xml',
        'reports/ple_inv_bal_report.xml',
        'reports/ple_inv_bal_template.xml',
    ],

    'assets': {
        'web.report_assets_common': [
            'ple_inv_and_bal_0313/static/src/css/main.css',
        ]
    },

    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 25.00
}
