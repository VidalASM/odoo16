# -*- coding: utf-8 -*-
{
    'name': "POS Discount Limit",
    'summary': """
        This module is allow to restrict discount limit on product and product category | POS Discount limit on product | Discount limit on product category | POS Product discount limit""",
    'description': """
        This module is used to restrict the discount limit on product and product category.""",    
    'version': '2.0',
    'author': "Preway IT Solutions",
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'views/product_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pw_discount_limit/static/src/js/**/*',
            "pw_discount_limit/static/src/xml/**/*.xml",
        ],
    },
    'images':[
        'static/description/banner.png',
    ],
    'price': 15.0,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    "license": "LGPL-3",
    "images":["static/description/Banner.png"],
}
