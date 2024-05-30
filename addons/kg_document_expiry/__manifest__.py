# -*- coding: utf-8 -*-
{
    "name": "Document Expiry",
    "summary": "Set Expiry Date for Document",
    "version": "16.0.1.0.0",
    'category': 'Productivity/Documents',
    'author': "Klystron Global",
    'maintainer': "Klystron Global",
    "license": "OPL-1",
    'website': 'https://www.klystronglobal.com',

    "depends": ["web", "documents", "hr"],
    "data": [
        'security/ir.model.access.csv',
        'views/email_template.xml',
        'views/documents_views.xml',
        # 'views/document_inspector.xml',
        'views/cron_jobs.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kg_document_expiry/static/src/js/document_expiry.js',
            'kg_document_expiry/static/src/views/**/*.xml',
        ],
    },
    'images': ['static/description/logo.png'],
    "installable": True,
}
