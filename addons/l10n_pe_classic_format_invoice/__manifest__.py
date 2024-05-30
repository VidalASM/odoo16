{
    'name': 'l10n pe fields for classic format invoice',
    'version': '16.0.3.3.8',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module will be used to make the classic invoice compatible for the Peruvian localization.',
    'category': 'All',
    "depends": [
        'account',
        'l10n_pe',
        'classic_format_invoice',
        'qr_code_on_sale_invoice',
        'account_exchange_currency'
    ],
    'data': [
        'views/classic_format_template.xml',
        'views/account_inherit.xml',
        'views/account_move_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
