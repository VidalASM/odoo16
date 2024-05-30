{
    'name': 'l10n pe format efact',
    'version': '16.0.0.3.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Add use format efact.',
    'category': 'All',
    'depends': [
        'account',
        'sale',
        'carrier_reference_number_invoice',
        'qr_code_on_sale_invoice',
        'l10n_latam_invoice_document',
        'account_price_unit_taxes_excluded',
        'amount_to_text',
        'l10n_pe_edocument',
        'l10n_pe_edi',
        'print_aditional_comment',

    ],
    'data': [
        "reports/report_efact.xml",
        "reports/report_efact_template.xml",
        "reports/report_ecotizacion.xml",
        "reports/report_ecotizacion_template.xml",
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 45.00
}
