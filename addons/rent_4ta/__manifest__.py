{
    'name': 'Renta de 4ta',
    'version': '16.0.0.1.3',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Allow issuing txt files of receipts for fees to declare in the Plame.',
    'description': 'Allow issuing txt files of receipts for fees to declare in the Plame.',
    'category': 'Payroll',
    'depends': [
        'contacts',
        'account',
        'tributary_address_extension',
        'first_and_last_name',
        'l10n_pe_edi',
        'ple_purchase_book', 
        'l10n_pe_advance_global_discount'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/account_tax_data.xml',
        'views/res_partner_views.xml',
        'views/rent_4ta_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}