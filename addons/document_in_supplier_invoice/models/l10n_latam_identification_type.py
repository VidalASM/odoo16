from odoo import models, fields, api


class L10nLatamDocumentType(models.Model):
    _inherit = 'l10n_latam.document.type'

    account_journal_id = fields.Many2one(
        'account.journal',
        string='Diario de Compras',
        help="""
            Debes escoger un diario de compras, solamente si este tipo de documento debe aparecer como opción 
            en los comprobantes y rectificativos de proveedor. Si este documento no se utiliza en compras, 
            debes dejar este campo vacío.
        """,
        domain="[('type', '=', 'purchase')]",
        company_dependent=True
    )

    account_journal_id_sale = fields.Many2one(
        comodel_name='account.journal',
        string='Diario de Ventas',
        help="""
            Debes escoger un diario de ventas, solamente si este tipo de documento debe aparecer como opción 
            en los comprobantes y rectificativos de clientes. Si este documento no se utiliza en ventas, 
            debes dejar este campo vacío.
        """,
        domain="['&', ('type', '=', 'sale'), ('l10n_latam_use_documents', '=', False)]",
        company_dependent=True
    )