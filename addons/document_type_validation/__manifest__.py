{
    'name': 'Document Type',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'summary': 'it serves to relate and manage the type of document required by SUNAT (DNI, RUC, others) inherited object: l10n_latam.identification.type. Also, add validation, when saving a res.partner, and when making a change on the field "vat" or "document_type_id" from res.partner, which if it does not meet the conditions of the parameters in the new fields created above.',
    'description': """
    Sirve para relacionar y administrar el tipo de documento exitigo por SUNAT ( DNI, RUC; otros)
    - OBJETO HEREDADO: l10n_latam.identification.type
    Además, añadir la validación, al guardar un res.partner, y al hacer un cambio sobre el campo “vat”, o “document_type_id” del res.partner, que si no cumple las condiciones de los parámetros en los nuevos campos creados arriba.
    """,
    'category': 'All',
    'depends': ['l10n_latam_base'],
    'data': [
        'views/l10n_latam_identification_type_view.xml',
        'views/partner_views.xml'
    ],
    "assets": {
        "web.assets_backend": [
            "document_type_validation/static/src/css/classes.css",
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
