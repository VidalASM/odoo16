{
    'name': 'Address origin and destiny in the lines',
    'version': '16.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': '''
        this module will create the necessary fields to bring the address of origin and destination different from that of the client and company.
    ''',
    'category': 'All',
    'depends': [
                'base',
                'account',
                ],
    'data': [
        'views/account_move_line_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
