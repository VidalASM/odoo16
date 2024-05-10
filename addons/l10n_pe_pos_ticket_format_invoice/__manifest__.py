{
    "name": "Electronic invoicing for Peru",
    "version": "16.0.0.0.0",
    "author": "Ganemo",
    "website": "https://www.ganemo.co/",
    "summary": "technical module to remove dependency of the module 'pos_ticket_format_invoice' all peruvian localization.",
    "description": """
    technical module to remove dependency of the module 'pos_ticket_format_invoice' all peruvian localization
    """,
    "category": "Point of Sale",
    "depends": [
        "pos_ticket_format_invoice",
        "qr_code_on_sale_invoice",
    ],
    "data": [
        "reports/pos_ticket_format.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 0.00,
}
