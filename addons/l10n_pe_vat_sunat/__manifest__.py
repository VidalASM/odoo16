# -*- coding: utf-8 -*-
{
    'name': "Actualizar RUC y DNI",

    'summary': """
        Actualiza RUC desde el portal SUNAT
        """,

    'description': """
        Este modulo devuelve información desde el portal SUNAT y ademas se puede configurar para obtener
        los representantes legales asi como los locales anexos.
    """,

    'author': "Codex Development",
    'website': "www.perucodex.com",

    'category': 'Localization/Peruvian',
    'version': '0.1',

    #Licence
    'license': 'LGPL-3',
    
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'base_vat', 
        'l10n_latam_base',
        'l10n_pe',
    ],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
        'views/res_partner_view.xml',
    ],
    'images': ['static/description/banner.gif'],
}