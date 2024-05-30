{
    'name': 'Use classic format to print stock picking',
    'version': '16.0.2.0.5',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Add an additional, classic-style stock picking peruvian format.',
    'Description': """
    Add a peruvian classic format for stock picking, which is requested by many users
    """,
    'category': 'Warehouse',
    'depends': [
        'account',
        'stock',
        'l10n_latam_invoice_document',
        'stock_picking_print_note',
        'invoice_type_document_extension',
        'third_parties_delivery',
    ],
    'assets': {'web.report_assets_common':
                   ['l10n_pe_classic_format_picking/static/src/css/main.css']},
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
