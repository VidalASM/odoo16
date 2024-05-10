{
    'name': 'Libro kardex valorizado PLE - SUNAT (Perú)',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co/ple',
    'summary': 'Valuated permanent inventory record (Valued kardex)',
    'description': """
    It issues the valued permanent inventory book that is mandatory for Peruvian companies 
    that invoice above 1500 UIT. You can generate the .txt file to directly present through 
    the electronic book program (PLE-SUNAT).
    """,
    'category': 'Accounting',
    'data': [
        'views/ple_report_stock_valuation_book_views.xml',
    ],
    'depends': [
        'ple_permanent_inventory_in_physical_units',
        'invoice_type_document_extension'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 399.00
}