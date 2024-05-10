{
    'name': ' account exchange currency',
    'version': '16.0.2.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': """
     Allows you to store the exchange rate value in the invoice, which is updated according to the date and currency.
     This type of exchange is the same that Odoo uses to convert the values into the company's currency, but we make 
     it visible on the invoice and store it, which allows it to be easily obtained in a report. We recommend that 
     modules that require knowing the exchange rate of Invoices for reporting use this module as a dependency. 
     The exchange rate format is the reverse of Odoo. Ex .: "3.652',
    """,
    'category': 'Accounting',
    'depends': ['account'],
    'data': ['views/account_move_views.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
