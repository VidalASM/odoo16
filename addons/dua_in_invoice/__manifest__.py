{
    'name': 'DUA in invoice',
    'version': '16.0.0.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': """
    Add required fields on purchase invoices to register the DUA as required by the electronic purchase record (PLE).
    """,
    'category': 'Accounting',
    'depends': [
        'localization_menu',
        'purchase_document_type_validation'
    ],
    'data': ['views/move_views.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 00.00
}
