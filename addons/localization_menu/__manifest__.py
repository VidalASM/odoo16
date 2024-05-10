{
    'name': 'Localización menú',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Creates the main menus for the peruvian localization.',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_menuitem.xml',
        'views/account_spot_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
