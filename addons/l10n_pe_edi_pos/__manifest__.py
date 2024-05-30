###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

{
    "name": "Factura electronica POS",
    "version": "16.0.1.0.0",
    "author": "OPeru",
    "summary": "Electronic invoicing for Point of sale / Odoo Peru ",
    "website": "https://www.operu.pe/facturacion-electronica",
    "depends": [
        "base",
        "l10n_latam_base",
        "l10n_pe",
        "point_of_sale",
        "l10n_pe_edi_odoofact",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/pos_receipt_views_demo.xml",
        "views/res_config_settings_views.xml",
        "views/pos_receipt_views.xml",
    ],
    "test": [],
    "installable": True,
    "images": ["static/description/banner.png"],
    "assets": {
        "point_of_sale.assets": [
            "l10n_pe_edi_pos/static/src/js/core/models.js",
            "l10n_pe_edi_pos/static/src/js/core/Database.js",
            "l10n_pe_edi_pos/static/src/js/core/qrcode.js",
            "l10n_pe_edi_pos/static/src/js/Screens/Client/ClientDefault.js",
            "l10n_pe_edi_pos/static/src/js/Screens/Payment/PaymentInvoiceJournal.js",
            "l10n_pe_edi_pos/static/src/js/Screens/Payment/PaymentScreen.js",
            "l10n_pe_edi_pos/static/src/js/Screens/Receipt/ElectronicInvoice.js",
            # 'l10n_pe_edi_pos/static/src/js/Screens/Receipt/InvoiceOrder.js',
            # **al estar comentado "InvoiceOrder.js" activa la funcionalidad de la
            # impresion A4 en el POS**
            "l10n_pe_edi_pos/static/src/js/Screens/Receipt/order_receipt.js",
            # 'l10n_pe_edi_pos/static/src/js/Screens/Receipt/OdooFactReceipt.js',
            "l10n_pe_edi_pos/static/src/xml/Screens/PartnerListScreen/PartnerLine.xml",
            'l10n_pe_edi_pos/static/src/xml/Screens/PartnerListScreen/PartnerDetailsEdit.xml',
            "l10n_pe_edi_pos/static/src/xml/Screens/PartnerListScreen/PartnerListScreen.xml",
            "l10n_pe_edi_pos/static/src/xml/Screens/Payment/PaymentInvoiceJournal.xml",
            "l10n_pe_edi_pos/static/src/xml/Screens/Payment/PaymentScreen.xml",
            "l10n_pe_edi_pos/static/src/xml/Screens/Ticket/TicketScreen.xml",
            'l10n_pe_edi_pos/static/src/xml/Screens/Receipt/OdooFactReceipt.xml',
        ],
    },
    "live_test_url": "http://operu.pe/manuales",
    "license": "AGPL-3",
    "price": 119.00,
    "currency": "USD",
    "sequence": 1,
    "support": "modulos@operu.pe",
}
