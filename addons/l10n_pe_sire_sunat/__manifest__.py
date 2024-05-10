{
    'name': 'Format SIRE SUNAT (Book Sale and Purchase)',
    'version': '16.0.2.2.10',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module will generate the SIRE SUNAT format for the purchase and sales books.',
    'description': """
        This module will generate the SIRE SUNAT format for the purchase and sales books.
    """,
    'category': 'Accounting/Localizations',
    'depends': [
        'ple_sale_book',
        'ple_purchase_book'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/sire_purchase_complements_rate_wizard_views.xml',
        'wizards/sire_purchase_complements_wizard_views.xml',
        'wizards/sire_purchase_national_wizard_views.xml',
        'wizards/sire_purchase_not_domiciled_wizard_views.xml',
        'wizards/sire_sale_add_proposed_wizard_views.xml',
        'wizards/sire_sale_wizard_views.xml',
        'views/account_move_views.xml',
        'views/account_menuitem.xml',
        # TODO: these query files are already added by the ple_sale_book and ple_purchase_book module.
        'sql/get_tax_purchase.sql',
        'sql/get_tax.sql',
        'sql/validate_string.sql'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 200.00,
}
