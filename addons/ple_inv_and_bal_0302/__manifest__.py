{
    'name': 'Formato 3.2 Libro de Inventarios y Balances - Efectivo y Equivalente de Efectivo',
    'version': '16.0.0.0.3',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'description': """
This module creates the format 3.2 "cash and equivalents cash" of the electronic inventory and balance book.""",
    'summary': 'This module creates the format 3.2 "cash and equivalents cash" of the electronic inventory and balance book.',
    'category': 'Accounting',
    'depends': ['ple_inv_and_bal_0301', 'ple_cash_book', 'financial_entity_sunat_code'],
    'data': [
        'security/ir.model.access.csv',
        'views/ple_inv_bal_views_one.xml',
        'views/ple_inv_bal_initial_one_balances.xml',
        'reports/ple_inv_bal_report.xml',
        'reports/ple_inv_bal_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 25.00
}
