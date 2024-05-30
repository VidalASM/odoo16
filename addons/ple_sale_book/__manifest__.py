{
    'name': ' Electronic Sales Record (PLE)',
    'version': '16.0.0.0.3',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Submit your sales book to SUNAT through PLE.',
    'category': 'Accounting',
    'depends': [
        'l10n_country_filter',
        'account_origin_invoice',
        'dua_in_invoice',
        'account_exchange_currency',
        'l10n_pe',
    ],
    'data': [
        'data/account_tax_report_data.xml',
        'views/base_views.xml',
        'views/account_views.xml',
        'views/ple_sale_views.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'sql/get_tax.sql',
        'sql/validate_string.sql',
        'sql/validate_spaces.sql'
    ],
    'installable': True,
    'auto_install': False,
    'post_init_hook': '_link_tags_ids',
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 120.00
}
