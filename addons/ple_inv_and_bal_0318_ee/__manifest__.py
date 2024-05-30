{
    'name': 'Formato 3.18 Libro de Inventarios y Balances - Estado de flujos de efectivo - Método Directo (Enterprise)',
    'version': '16.0.1.0.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module creates the format 3.18 "Statement of cash flows - Direct method" of the electronic inventory and balance book. (Enterprise).',
    'description': 'This module creates the format 3.18 "Statement of cash flows - Direct method" of the electronic inventory and balance book. (Enterprise).',
    'category': 'Accounting',
    'depends': [
        'account_reports',
        'ple_inv_and_bal_0301',
        'ple_inv_and_bal_0320_ee',
        'l10n_pe_catalog'
    ],
    'data': [
        'data/ple_inv_bal_3_18_report.xml',
        'security/ir.model.access.csv',
        'reports/ir_actions_report.xml',
        'reports/ir_actions_report_templates.xml',
        'views/account_account_views.xml',
        'views/accout_move_line_views.xml',
        'wizards/wizard_report_txt_ple_3_18_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 50.00
}
