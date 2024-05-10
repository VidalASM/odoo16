{
    'name': 'Detractions with freight transport service',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'summary': 'This module will create fields necessary for to emit invoice with detractions freight transport service.',
    'category': 'All',
    'depends': [
        'l10n_pe_edocument',
        'address_origin_destiny_lines'
    ],
    'data': [
        'data/2.1/edi_templates.xml',
        'views/account_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 50.00
}
