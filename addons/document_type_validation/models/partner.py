from odoo import api, fields, models


def _validate_long(word, length, validation_type, field_name):
    if word and validation_type:
        if validation_type == 'exact':
            if len(word) != length:
                return "- La cantidad de caracteres para el campo '%s' debe ser: %d \n" % \
                       (field_name, length)
        elif validation_type == 'maximum':
            if len(word) > length:
                return "- La cantidad de caracteres para el campo '%s' debe ser como máximo: %d \n" % \
                       (field_name, length)
    return ''


def _validate_word_structure(word, validation_type, field_name):
    special_characters = '-°%&=~\\+?*^$()[]{}|@%#"/¡¿!:.,;'
    if word:
        if validation_type == 'other':
            return ''
        if validation_type == 'numeric':
            if not word.isdigit():
                return "- El campo '%s' solo debe contener números.\n" % field_name
            else:
                total = 0
                for d in str(word):
                    total += int(d)
                if total == 0:
                    return "- El campo '%s' no puede contener solo ceros.\n" % field_name
        special = ''
        for letter in word:
            if letter in special_characters:
                special += letter
        if special != '':
            return "- El campo '%s' contiene caracteres no permitidos:  %s \n" % (field_name, special)
    return ''


class ResPartner(models.Model):
    _inherit = 'res.partner'

    error_dialog = fields.Text(
        compute="_compute_error_dialog_partner",
        store=True,
        help='Campo usado para mostrar mensaje de alerta en el mismo formulario'
    )

    @api.depends('country_id', 'l10n_latam_identification_type_id', 'vat')
    def _compute_error_dialog_partner(self):
        latam_company = self.env.company.country_id in [self.env.ref('base.pe'), self.env.ref('base.ar'), self.env.ref('base.cl')]
        for rec in self:
            msg = ''
            if rec.l10n_latam_identification_type_id and rec.vat and latam_company:
                type_document_partner = rec.l10n_latam_identification_type_id.exact_length
                msg += _validate_long(
                    rec.vat,
                    rec.l10n_latam_identification_type_id.doc_length,
                    type_document_partner,
                    'Número Documento'
                )
                msg += _validate_word_structure(
                    rec.vat,
                    rec.l10n_latam_identification_type_id.doc_type,
                    'Número Documento'
                )
            rec.error_dialog = msg

    @api.onchange('vat', 'error_dialog')
    def _onchange_error_dialog_partner(self):
        for rec in self:
            if rec.error_dialog:
                error = rec.error_dialog
                rec.vat = False
                rec.error_dialog = error
