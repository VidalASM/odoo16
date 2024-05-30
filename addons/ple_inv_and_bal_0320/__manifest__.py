{
    'name': 'Formato 3.20 Libro Inventario y Balance - Estado de Resultados',
    'version': '16.0.0.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module creates the format 3.1 "Statement of income" of the electronic inventory and balance book.',
    'description': 'This module creates the format 3.1 "Statement of income" of the electronic inventory and balance book.',
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'ple_inv_and_bal_0301',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_account_views.xml',
        'views/ple_inv_bal_20_views.xml',
        'reports/ple_inv_bal_report.xml',
        'reports/ple_inv_bal_template.xml'
    ],
    'assets': {
        'web.report_assets_common': [
            'ple_inv_and_bal_0320/static/src/css/ple_inv_and_bal_0320.css',
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 50.00
}