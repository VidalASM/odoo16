{
    'name': 'Base Spot',
    'version': '16.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': """
        Create additional fields on purchase invoices that allow you to identify if an invoice is affected by legal deductions, the type of deduction, 
        the payment date of the deduction and the payment operation code of the deduction.
    """,
    'depends': ['localization_menu'],
    'data': [
        'data/account_spot_detraction_data.xml',
        'views/account_move_views.xml',
        'views/account_spot_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
