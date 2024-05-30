{
    'name': 'Formato 3.16.2 Libro de Inventarios y Balances - Estructura de la participación accionaria o de participaciones sociales',
    'version': '16.0.0.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'summary': 'This module creates the format 3.16.2 "Structure of the shareholding or company participations" of the electronic inventory and balance book',
    'description': 'This module creates the format 3.16.2 "Structure of the shareholding or company participations" of the electronic inventory and balance book',
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'financial_statement_annexes',
        'ple_inv_and_bal_0302',
        'ple_inv_and_bal_0316_01',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ple_inv_bal_views_02_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 35.00
}
