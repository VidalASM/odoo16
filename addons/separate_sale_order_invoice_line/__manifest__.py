{
    'name': 'Separate sale orden invoice line',
    'version': '16.0.0.0.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'description': """
This module will allow us to place 2 exchange rates on the same day.""",
    'summary': """
        This module will allow us to place 2 exchange rates on the same day.
    """,
    'category': 'Accounting',
    'depends': ['sale'],
    'data': ['wizards/sale_make_invoice_advance_views.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 40.00
}
