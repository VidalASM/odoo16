{
    'name': 'Formato 3.8 Libro de Inventarios y Balances - Inversiones Inmobiliarias',
    'version': '16.0.1.0.3',
    'author': 'Ganemo',
    'live_test_url': 'https://www.ganemo.co/demo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module creates the format 3.8 "securities investments" of the electronic inventory and balance book.',
    'description': """
This module creates the format 3.8 "securities investments" of the electronic inventory and balance book.""",
    'category': 'Accounting',
    'depends': ['ple_sale_book',
                'ple_inv_and_bal_0302',
                'asset_intangible',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_intangible_views.xml',
        'views/ple_inv_bal_views_08.xml',
        'views/ple_inv_bal_initial_balances.xml',
        'reports/ple_inv_bal_08_report.xml',
        'reports/ple_inv_bal_08_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 30.00
}
