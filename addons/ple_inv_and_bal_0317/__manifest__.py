{
    'name': 'Formato 3.17 Libro de Inventarios y Balances - Balance de Comprobación',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'description': """
This module creates the format 3.17 "checking balances" of the electronic inventory and balance book.""",
    'summary': 'This module creates the format 3.17 "checking balances" of the electronic inventory and balance book.',
    'category': 'Accounting',
    'depends': ['ple_sale_book',
                'l10n_pe_catalog'],
    'data': [
        'security/ir.model.access.csv',
        'views/trial_balance_catalog_views.xml',
        'data/trial_balances_codes.xml',
        'data/account_journal.xml',
        'views/ple_inv_bal_seventeen_views.xml',
        'views/balances_ple_inv_bal_seventeen.xml',
        'reports/ple_inv_bal_seventeen_report.xml',
        'reports/ple_inv_bal_seventeen_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'post_init_hook': '_update_data_trial_balances',
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 50.00
}
