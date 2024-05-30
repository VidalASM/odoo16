{
    'name': 'Invoice for A4 pre printed format',
    'version': '16.0.0.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': ' Add invoice information to a blank document, to be used with pre-printed layout formats.',
    'category': 'Accounting',
    'depends': [
        'account',
        'amount_to_text',
        'l10n_latam_invoice_document',
        'base_address_extended',
    ],
    'data': [
        "reports/invoice_preprinted_report.xml",
        "reports/invoice_preprinted_template.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "invoice_a4_preprinted_format/static/src/css/style_delivery_note.css",
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 125.00
}