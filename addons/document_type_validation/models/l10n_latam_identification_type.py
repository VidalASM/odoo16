from odoo import fields, models


class L10nLatamIdentificationType(models.Model):
    _inherit = 'l10n_latam.identification.type'

    doc_length = fields.Integer(
        string='Longitud'
    )
    doc_type = fields.Selection(
        selection=[
            ('numeric', 'Númerico'),
            ('alphanumeric', 'Alfanúmerico'),
            ('other', 'Otros')],
        string='Tipo'
    )
    exact_length = fields.Selection(
        selection=[
            ('exact', 'Exacta'),
            ('maximum', 'Máxima')],
        string='Longitud Exacta'
    )
    nationality = fields.Selection(
        selection=[
            ('national', 'Nacional'),
            ('foreign', 'Extranjero'),
            ('both', 'Ambos')],
        string='Nacionalidad'
    )
