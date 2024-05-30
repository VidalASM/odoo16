from odoo import fields, models


class L10nLatamIdentificationType(models.Model):
    _inherit = 'l10n_latam.identification.type'

    description = fields.Char(
        translate=True
    )
