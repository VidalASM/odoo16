from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_pe_cis_client_id = fields.Char(
        string='Client ID de la consulta CPE',
    )
    l10n_pe_cis_client_secret = fields.Char(
        string='Client Secret de la consulta CPE',
    )
