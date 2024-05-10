{
    'name': 'Formato 3.7 Libro de Inventarios y Balances - Mercaderías y Productos Terminados',
    'version': '16.0.0.0.3',
    'author': 'Ganemo',
    'license': 'Proprietary',
    'website': 'https://www.ganemo.co',
    'description':'''This module creates the format 3.7 "merchandise and finished products" of
                    the electronic inventory and balance book''',
    'summary': 'This module creates the format 3.7 "merchandise and finished products" of the electronic inventory and balance book',
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'ple_permanent_inventory_in_physical_units',
        'ple_inv_and_bal_0302',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ple_initial_balances_07.xml',
        'views/ple_inv_bal_views_02_inherit.xml',
        'reports/ple_inv_bal_report.xml',
        'reports/ple_inv_bal_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 35.00
}
