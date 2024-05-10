{
    'name': 'Pagos masivos de detracciones',
    'version': '16.0.0.1.7',
    'author': 'Ganemo, Unoobi',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'summary': 'This module allows us to make massive payments of detractions.',
    'category': 'Accounting',
    'depends': [
        'l10n_pe_edi',
        'base_spot',
        'account',
        'account_batch_payment',
        'account_field_to_force_exchange_rate',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/account_batch_payment.xml',
        'wizard/account_payment_register.xml',
        'wizard/account_move_detractions.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'txt_detractions/static/src/views/list/list_renderer.js',
        ],

    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 299.00
}
