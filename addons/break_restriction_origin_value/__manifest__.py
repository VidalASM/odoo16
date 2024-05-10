{
    'name': 'To break restriction exchange rates on the same day',
    'version': '16.0.0.2.4',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': '''
        This module will force to be able to place the amount in currency
        of the accounting notes and to make an automatic change in the currency 
        field when an asset is registered from suppliers.
    ''',
    'Description': '''
        This module will force to be able to place the amount in currency
        of the accounting notes and to make an automatic change in the currency 
        field when an asset is registered from suppliers.
    ''',
    'category': 'Accounting',
    'depends': ['account', 'account_asset', 'account_field_to_force_exchange_rate'],
    'data': [
        'views/account_asset_views.xml',    
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}