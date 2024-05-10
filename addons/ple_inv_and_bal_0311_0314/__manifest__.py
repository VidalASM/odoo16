{
    'name': 'Formato 3.11 Libro de Inventarios y Balances - Remuneraciones y participaciones por pagar y Formato 3.14 Libro de inventarios y Balances - Beneficios de los Trabajadores',
    'version': '16.0.1.0.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module creates the format 3.11 "remunerations and shares payable" of the electronic inventory and balance book.',
    'description': 'This module creates the format 3.11 "remunerations and shares payable" of the electronic inventory and balance book.',
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'financial_statement_annexes',
        'ple_inv_and_bal_0302',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ple_inv_bal_11_14_views.xml',
        'reports/ple_inv_bal_report.xml',
        'reports/ple_inv_bal_template_11.xml',
        'reports/ple_inv_bal_template_14.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 25.00
}
