{
    'name': 'Formato 3.9  Libro de Inventarios y Balances - Intangibles',
    'version': '16.0.0.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'description': 'This module creates the format 3.9 "intangible assets" of the electronic inventory and balance book.',
    'summary': 'This module creates the format 3.9 "intangible assets" of the electronic inventory and balance book.',
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'ple_inv_and_bal_0301',
        'ple_cash_book',
        'ple_inv_and_bal_0302',
        'asset_intangible'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ple_inv_bal_views_09.xml',
        'reports/ple_inv_bal_09_report.xml',
        'reports/ple_inv_bal_09_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 30.00
}
