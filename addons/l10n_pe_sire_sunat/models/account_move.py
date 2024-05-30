from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_pe_is_complement_sire = fields.Boolean(
        string='Complemento para SIRE',
        help='Si este registro es un CPE físico deberás activar este campo para poder generar el TXT de complemento.'
    )
