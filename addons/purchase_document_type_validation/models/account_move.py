from odoo import api, models, fields
from odoo.exceptions import ValidationError
import re

type_validation = [
    ('numbers', 'Numérico'),
    ('letters', 'Alfanumérico'),
    ('no_validation', 'Sin validación')
]

length_validation = [
    ('equal', 'Igual'),
    ('max', 'Hasta'),
    ('no_validation', 'Sin validación')
]


def _validate_long(word, length, validation_type, field_name):
    if word and validation_type:
        if validation_type == 'equal':
            if len(word) != length:
                return "- La cantidad de caracteres para el campo '%s' debe ser: %d \n" % \
                       (field_name, length)
        elif validation_type == 'max':
            if len(word) > length:
                return "- La cantidad de caracteres para el campo '%s' debe ser como máximo: %d \n" % \
                       (field_name, length)
    return ''


def _validate_word_structure(word, validation_type, field_name):
    special_characters = '-°%&=~\\+?*^$()[]{}|@%#"/¡¿!:.,;'
    if word:
        if validation_type == 'numbers':
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


class InvoiceDocumentType(models.Model):
    _inherit = 'l10n_latam.document.type'

    prefix_long = fields.Integer(string='Longitud Serie')
    prefix_length_validation = fields.Selection(
        selection=length_validation,
        string='Validacion Longitud Serie',
        default='no_validation'
    )
    prefix_validation = fields.Selection(
        selection=type_validation,
        string='Validación Serie',
        default='no_validation'
    )
    correlative_long = fields.Integer(string='Longitud Correlativo')
    correlative_length_validation = fields.Selection(
        selection=length_validation,
        string='Validación Longitud Correlativo',
        default='no_validation'
    )
    correlative_validation = fields.Selection(
        selection=type_validation,
        string='Validación Correlativo',
        default='no_validation'
    )


class AccountMove(models.Model):
    _inherit = 'account.move'

    error_dialog = fields.Text(
        compute="_compute_error_dialog",
        store=True,
        help='Campo usado para mostrar mensaje de alerta en el mismo formulario'
    )
    l10n_pe_sunat_code = fields.Char(
        related='l10n_latam_document_type_id.code',
        string='Código Sunat'
    )
    internal_type = fields.Selection(
        related='l10n_latam_document_type_id.internal_type',
        string='Internal Type',
        readonly=True
    )
    
    @api.depends('l10n_latam_document_type_id', 'move_type', 'ref')
    def _compute_error_dialog(self):
        for rec in self:
            if rec.move_type not in ['out_invoice', 'out_refund'] and rec.name:
                msg = ''
                if isinstance(rec.ref, str):
                    ref_code = re.search(r'\((.*?)\)', rec.ref)
                    if ref_code:
                        rec.ref = ref_code.group(1)
                reference = rec.ref
                if reference and '-' in reference and len(reference.split('-')) == 2 and rec.l10n_latam_document_type_id:
                    serie, correlative = reference.split('-')
                    type_document_serie = rec.l10n_latam_document_type_id.prefix_length_validation

                    type_document_correlative = rec.l10n_latam_document_type_id.correlative_length_validation
                    msg += _validate_long(serie, rec.l10n_latam_document_type_id.prefix_long, type_document_serie, 'Serie')
                    msg += _validate_long(correlative, rec.l10n_latam_document_type_id.correlative_long, type_document_correlative, 'Correlativo')

                    msg += _validate_word_structure(serie, rec.l10n_latam_document_type_id.prefix_validation, 'Serie')
                    msg += _validate_word_structure(correlative, rec.l10n_latam_document_type_id.correlative_validation, 'Correlativo')
                else:
                    if rec.move_type != 'entry' and reference and '-' in reference and len(reference.split('-')) != 2:
                        msg += 'Formato de referencia de proveedor incorrecto. Debe ser de la siguiente forma para que pueda continuar con el proceso: FXXX-XXXXXXXX'
                rec.error_dialog = msg

    @api.constrains('error_dialog', 'move_type')
    def _constrains_error_dialog(self):
        for rec in self:
            if rec.move_type not in ['out_invoice', 'out_refund'] and rec.error_dialog:
                raise ValidationError('Debe resolver las siguientes requerimientos antes de guardar: \n %s' % rec.error_dialog)
