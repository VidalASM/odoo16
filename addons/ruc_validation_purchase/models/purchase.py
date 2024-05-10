from odoo import models, fields
from datetime import datetime
from odoo.exceptions import ValidationError
import pytz


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

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
    message_response = fields.Text(string='Mensaje de respuesta')
    code_country_company = fields.Char(
        string='Código de la compañía logeada',
        store=True,
        related='company_id.country_id.code'
    )


    def action_ruc_validation_sunat(self):
        obj_partner = self.partner_id
        obj_partner.action_ruc_validation_sunat()
        message_response = ''
        if obj_partner.l10n_latam_identification_type_id.l10n_pe_vat_code == '6':
            if not self.date_order:
                raise ValidationError('Incorrecto, ingrese fecha de compra.')

            if obj_partner.condition_contributor_sunat == 'HABIDO' and obj_partner.state_contributor_sunat == 'ACTIVO':
                self.active_and = 'done'
            else:
                self.active_and = 'blocked'

            state_contributor_sunat = obj_partner.state_contributor_sunat
            condition_contributor_sunat = obj_partner.condition_contributor_sunat
            date_today = datetime.now()
            date_purchase = self.date_order
            date_residue = date_today - date_purchase
            more_values = ''
            if date_residue.days > 30:
                more_values = 'que tiene una diferencia mayor a 30 días de la fecha de la compra, por ese motivo' \
                              ' recomendamos que verifique la "información histórica" en la "Consulta RUC" de su proveedor y' \
                              ' verifique si en dicha fecha se encontraba HABIDO para la emisión de comprobantes.'

            date_today = self._convert_date_timezone(date_today, '%Y-%m-%d')
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

    def _convert_date_timezone(self, date_order, format_time='%Y-%m-%d %H:%M:%S'):
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        if date_order:
            date_tz = pytz.utc.localize(date_order).astimezone(tz)
            date_order = date_tz.strftime(format_time)
        return date_order

    def button_confirm(self):
        if self.active_and == 'done' or self.code_country_company != 'PE':
            super(PurchaseOrder, self).button_confirm()
        else:
            raise ValidationError('Documento compra debe estar activo y habido.')
        return True
