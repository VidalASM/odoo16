{
    'name': 'Print aditional comment',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'category': 'All',
    'summary': '''
    Add a field in the company configuration, which is rich text so that what we fill in that field will appear printed on the Sales Invoice, 
    above the "Terms and Conditions" field.
    ''',
    'depends': ['account'],
    'data': [
        'views/qweb_templates.xml',
        'views/res_company_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
