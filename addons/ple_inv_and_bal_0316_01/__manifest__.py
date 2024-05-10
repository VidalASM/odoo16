{
    'name': 'Formato 3.16.1 Libro de Inventarios y Balances - Capital',
    'version': '16.0.0.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module creates the format 3.16.1 "Capital" of the electronic inventory and balance book',
    'description': 'This module creates the format 3.16.1 "Capital" of the electronic inventory and balance book',
    'category': 'Accounting',
    'depends': ['ple_sale_book', 'financial_statement_annexes', 'ple_inv_and_bal_0302'],
    'data': [
        'security/ir.model.access.csv',
        'views/ple_inv_bal_views_02_inherit.xml',
        'views/res_company.xml',
        'views/fields_report_031601.xml',
        'reports/ple_inv_bal_06_report.xml',
        'reports/ple_inv_bal_06_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 35.00
}


