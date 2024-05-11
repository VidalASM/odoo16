# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Signature by Salesperson in Sales Order',
    'version': '16.0.0.0',
    'category': 'Sales',
    'summary': 'salesperson signature in sales order digital signature by salesperson signature sales documents salesperson sign digital sign sales document by salesperson signature note upload signature salesperson digitally sign sales orders',
    "description": """The Signature by Salesperson in Sales Order Odoo app enables salespersons to digitally sign sales orders directly within the Odoo platform. This signature serves as verification and confirmation of their involvement in the sales process, adding a layer of authenticity to the transaction. By requiring a salesperson's signature before a sales order is finalized, businesses can ensure that the order has been reviewed and approved by the responsible sales representative.""",
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'depends': ['sale_management'],
    'data': [
        'views/inherit_sale_order.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    "images":['static/description/Signature-by-Salesperson-in-SO-Banner.gif'],
    'live_test_url':'https://youtu.be/2T4Uuw6_qRI',
}
