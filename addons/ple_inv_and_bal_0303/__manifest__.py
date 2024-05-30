{
    'name': 'Formato 3.3 Libro de Inventarios y Balances - Cuentas por Cobrar Comerciales de Terceros y Relacionadas',
    'version': '16.0.0.0.7',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module creates the format 3.3 “accounts receivable” of the electronic inventory and balance book.',
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'financial_statement_annexes',
        'ple_inv_and_bal_0302',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ple_inv_bal_inherit_0302.xml',
        'reports/ple_inv_bal_03_report.xml',
        'reports/ple_inv_bal_03_template.xml',
    ],
    "assets": {
        "web.report_assets_common": [
            "ple_inv_and_bal_0303/static/src/css/main.css",
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 25.00
}
