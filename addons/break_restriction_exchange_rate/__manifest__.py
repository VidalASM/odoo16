{
    'name': "To break restriction exchange rates on the same day",
    'version': '16.0.0.0.0',
    'author': "Ganemo",
    'website': "https://www.ganemo.co",
    'live_test_url': 'https://www.ganemo.co/demo',
    'description': "This module will allow us to place 2 exchange rates on the same day.",
    'summary': "This module will allow us to place 2 exchange rates on the same day",
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'data/no_res_currency_rate.xml'
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'Other proprietary',
    'price': 0.00,
}
