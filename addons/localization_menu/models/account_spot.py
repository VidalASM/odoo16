from odoo import fields, models


class AccountSpotRetention(models.Model):
    _name = 'account.spot.retention'
    _description = 'SPOT Retention'

    name = fields.Char(
        string='Nombre',
        required=True
    )


class AccountSpotDetraction(models.Model):
    _name = 'account.spot.detraction'
    _description = 'SPOT Detraction'

    name = fields.Char(
        string='Nombre',
        required=True
    )


class CodeAduana(models.Model):
    _name = 'code.aduana'
    _description = 'Customs Unit Code (Customs)'

    name = fields.Char(
        string='Descripción',
        required=True
    )
    code = fields.Char(
        string='Código',
        required=True
    )
