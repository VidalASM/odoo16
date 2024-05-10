{
    'name': 'Accounting ledger PLE - SUNAT (Perú)',
    'version': '16.0.0.3.6',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co/ple',
    'summary': 'Accounting ledger PLE - SUNAT (Perú)',
    'description': """
        It generates the electronic ledger that is mandatory for companies that must keep complete accounting in Peru.
        It is very easy, Odoo generates the .txt ready to download and present to SUNAT through the electronic book program (PLE).
    """,
    'category': 'Accounting',
    'depends': [
        'ple_sale_book',
        'invoice_type_document',
        'ple_purchase_book'
    ],
    'data': [
        'views/ple_ledger_views.xml',
        'security/ir.model.access.csv',
        'sql/get_data_structured_ledger.sql',
        'sql/string_ref.sql',
        'sql/UDF_numeric_char_ledger.sql',
        'sql/get_journal_correlative.sql',
        'sql/get_data_structured_sire.sql'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 160.00
}
