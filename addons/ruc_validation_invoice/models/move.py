from odoo import models, fields
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    active_and = fields.Selection(
        selection=[
            ('normal', 'Por Validar con SUNAT'),
            ('done', 'Proveedor está Habido y Activo'),
            ('blocked', 'Proveedor No está Habido y Activo')
        ],
        help="Este campo es autocompletado según el Resultado de la consulta RUC,"
             "deberá estar de color verde para que la factura sea Validada. En la Pestaña 'Otra información'"
             "puedes encontrar el mensaje que la consulta RUC ha generado en relación a este campo."
             "Para forzar la validación, este campo puede ser cambiado manualmente.",
        string='Activo y Habido',
        default='normal'
    )
    related_require_validation_ruc = fields.Boolean(
        string='Requiere validación RUC',
        related='l10n_latam_document_type_id.require_validation_ruc',
        store=True
    )
    message_response = fields.Text(string='Mensaje de respuesta')

    def action_ruc_validation_sunat(self):
        obj_partner = self.partner_id
        obj_partner.action_ruc_validation_sunat()
        message_response = ''
        if obj_partner.l10n_latam_identification_type_id.l10n_pe_vat_code == '6':
            if not self.invoice_date:
                raise ValidationError('Incorrecto, ingrese fecha de factura.')

            if obj_partner.condition_contributor_sunat == 'HABIDO' and obj_partner.state_contributor_sunat == 'ACTIVO':
                self.active_and = 'done'
            else:
                self.active_and = 'blocked'

            state_contributor_sunat = obj_partner.state_contributor_sunat
            condition_contributor_sunat = obj_partner.condition_contributor_sunat
            date_today = fields.Date.today()
            date_invoice = self.invoice_date
            date_residue = date_today - date_invoice
            more_values = ''
            if date_residue.days > 30:
                more_values = 'que tiene una diferencia mayor a 30 días de la fecha de la factura, por ese motivo' \
                              ' recomendamos que verifique la "información histórica" en la "Consulta RUC" de su proveedor y' \
                              ' verifique si en dicha fecha se encontraba HABIDO para la emisión de comprobantes.'

            message_response = 'Al momento de realizar la Consulta RUC del comprobante, el estado de contribuyente de este proveedor' \
                               ' es {} y su condición de contribuyente es {}. La fecha de consulta fue {}. {}'.format(state_contributor_sunat,
                                                                                                                      condition_contributor_sunat,
                                                                                                                      date_today,
                                                                                                                      more_values
                                                                                                                      )
        else:
            self.active_and = 'normal'

        self.message_response = message_response
        return True

    def action_post(self):
        to_open_invoices = self.filtered(lambda inv: inv.state == 'draft')
        if to_open_invoices.filtered(lambda x: x.related_require_validation_ruc and x.active_and != 'done'):
            raise ValidationError('Si Tipo de documento require validación RUC entonces verifique campo: activo y habido.')
        return super(AccountMove, self).action_post()


class InvoiceDocumentType(models.Model):
    _inherit = 'l10n_latam.document.type'

    require_validation_ruc = fields.Boolean(string='Require validación RUC')
