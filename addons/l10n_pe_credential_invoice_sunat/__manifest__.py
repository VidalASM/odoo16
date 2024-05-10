{
    'name': 'Credential Invoice SUNAT',
    'version': '16.0.2.1.3',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module will validate the status of the invoice through the integrated query.',
    'category': 'Accounting/Localizations',
    'description': """
This module will validate the status of the invoice through the integrated query.
    """,
    'depends': ['account'],
    'data': [
        'data/cron_data.xml',
        'views/res_company_views.xml',
        'views/account_move_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'currency': 'USD',
    'price': 50.00,
    'license': 'Other proprietary',
}