{
    'name': 'Use classic format to print invoices',
    'version': '16.0.1.8.6',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': '''
    Add an additional, classic-style invoice format.
    ''',
    'Description': '''
    Add a classic format for invoices, which is requested by many users
    ''',
    'category': 'Accounting',
    'depends': [
        'account',
        'uom',
        'l10n_latam_invoice_document',
        'carrier_reference_number_invoice',
        'print_aditional_comment',
        'amount_to_text',
        'base_address_extended',
        'aditional_document_reference',
    ],
    'assets': {
        'web.report_assets_common': [
            'classic_format_invoice/static/src/css/main.css',
        ]},
    'data': [
        "reports/ticket_report.xml",
        "reports/ticket_template.xml",
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 45.00
}
