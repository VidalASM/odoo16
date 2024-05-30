{
    'name': 'fields reason and charge for invoice',
    'version': '16.0.0.1.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module will validate the status of the invoice through the integrated query.',
    'category': 'Accounting',
    "depends": [
        'l10n_pe_classic_format_invoice',
        'l10n_pe_advance_global_discount'
    ],
    'data': [
        'data/2.1/edi_templates.xml',
        'views/l10n_pe_reason_charge_view.xml',
        'views/account_move_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'uninstall_hook': '_refactor_xml',
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
