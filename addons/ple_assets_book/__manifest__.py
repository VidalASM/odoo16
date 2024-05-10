{
    'name': 'Reporte PLE assets book',
    'version': '16.0.1.0.7',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': """""",
    'depends': [
        'merch_and_model_asset',
        'ple_sale_book',
        'account_asset',
        'break_restriction_origin_value',
    ],
    'data': [
        'views/account_views.xml',
        'views/account_assets.xml',
        'views/ple_report_assets_book_views.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'price': 299.00
}
