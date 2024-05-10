{
    'name': 'Electronic Purchase Record',
    'version': '16.0.0.0.9',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Generate your Electronic Purchase Record for PLE SUNAT',
    'description': 'Create the e-book of Purchases to present to the PLE SUNAT. We always maintain it and keep it updated',
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'base_spot',
        'document_in_supplier_invoice',
        'l10n_pe_catalog',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/account_tax_report_data.xml',
        'data/account_tax_group_data.xml',
        'data/account_tax_data.xml',
        'data/product_template_data.xml',
        'data/account_move_data.xml',
        'data/multicompany_autolinked.xml',
        'data/tags_autolink.xml',
        'views/ple_purchase_views.xml',
        'views/move_views.xml',
        'sql/get_tax_purchase.sql'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 160.00
}
