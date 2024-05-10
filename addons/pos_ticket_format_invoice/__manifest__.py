{
    "name": "Use POS ticket format to print invoices",
    "version": "16.0.0.6.3",
    "author": "Ganemo",
    "website": "https://www.ganemo.co/",
    "summary": "Add an additional format to invoices, POS ticket type, which allows the use of thermal printers.",
    "description": """
    Use ticket format to print invoices. It is the format that points of sale usually use and can be printed on thermal printers
    """,
    "category": "Point of Sale",
    "depends": [
        "account",
        "l10n_latam_invoice_document",
        "print_aditional_comment",
        'amount_to_text',
        'base_address_extended',
    ],
    "data": [
        "reports/ticket_report.xml",
        "reports/ticket_template.xml",
        "views/account_journal.xml"
    ],
    'assets': {
        'web.report_assets_common': [
            'pos_ticket_format_invoice/static/src/css/main.css',
        ],
    },
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 45.00,
}
