import json
import requests
import pytz
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_pe_cis_query_status = fields.Boolean(
        string='Estado de la consulta CPE',
        readonly=True
    )
    l10n_pe_cis_state = fields.Selection(
        selection=[
            ('for_confirmed', 'Por Confirmar'),
            ('exception', 'Excepción'),
            ('confirmed', 'Confirmado')],
        string='Validación de la consulta CPE',
        default='for_confirmed',
        readonly=True
    )
    l10n_pe_cis_cpe_status = fields.Selection(
        selection=[
            ('0', 'No Existe'),
            ('1', 'Aceptado'),
            ('2', 'Anulado'),
            ('3', 'Autorizado'),
            ('4', 'No Autorizado')
        ],
        string='Estado del comprobante de la consulta CPE',
        readonly=True
    )
    l10n_pe_cis_taxpayer_status = fields.Selection(
        selection=[
            ('00', 'Activo'),
            ('01', 'Baja Provisional'),
            ('02', 'Baja Prov. Por Oficio'),
            ('03', 'Suspensión Temporal'),
            ('10', 'Baja Definitiva'),
            ('11', 'Baja De Oficio'),
            ('22', 'Inhabilitado-Vent.Única')
        ],
        string='Estado del contribuyente de la consulta CPE',
        readonly=True
    )
    l10n_pe_cis_taxpayer_domiciliary_status = fields.Selection(
        selection=[
            ('00', 'Habido'),
            ('09', 'Pendiente'),
            ('11', 'Por Verificar'),
            ('12', 'No Habido'),
            ('20', 'No Hallado')
        ],
        string='Condición domiciliaria de la consulta CPE',
        readonly=True
    )

    def _l10n_pe_cis_get_credentials(self, company):
        self.ensure_one()
        if not company.l10n_pe_cis_client_id:
            raise ValidationError('Debe configurar previamente su Client ID en la configuración de la compañia: {}.'.format(company.name))
        if not company.l10n_pe_cis_client_secret:
            raise ValidationError('Debe configurar previamente su Client Secret en la configuración de la compañia: {}.'.format(company.name))
        return {
            'client_id': company.l10n_pe_cis_client_id,
            'client_secret': company.l10n_pe_cis_client_secret
        }

    def _l10n_pe_cis_get_token(self, credentials):
        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        url = 'https://api-seguridad.sunat.gob.pe/v1/clientesextranet/{}/oauth2/token/'.format(client_id)
        credentials_data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.sunat.gob.pe/v1/contribuyente/contribuyentes',
            'client_id': client_id,
            'client_secret': client_secret
        }
        try:
            sunat_client = requests.post(url, data=credentials_data)
            response_data = json.loads(sunat_client.text)
            if 'error_description' in response_data:
                raise ValidationError(response_data['error_description'])
            return response_data['access_token']
        except requests.HTTPError:
            raise ValidationError('Error al establece la conexión.')
        except json.decoder.JSONDecodeError:
            raise ValidationError('Error en la obtención de datos. Intente de nuevo.')

    def _l10n_pe_cis_validate_invoice_data(self):
        valid_move_state = ['posted', 'cancel']
        valid_move_types = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
        
        if self.state not in valid_move_state:
            raise ValidationError('Para realizar la consulta, la factura debe estar en estado "Publicado" o "Cancelado".')
        if self.move_type not in valid_move_types:
            raise ValidationError('Este tipo de factura no es válido para realizar la consulta')
        
        if not self.invoice_date:
            raise ValidationError('Debe ingresar la fecha de la factura.')
        if not self.l10n_latam_document_type_id:
            raise ValidationError('Debe configurar el tipo de documento de la factura.')

    def _l10n_pe_cis_get_invoice_number(self):
        if self.move_type in ['out_invoice', 'out_refund']:
            invoice_number = self.name.replace(' ', '').split('-') if self.name and '-' in self.name else ''
        elif self.move_type in ['in_invoice', 'in_refund']:
            invoice_number = self.ref.replace(' ', '').split('-') if self.ref and '-' in self.ref else ''
        else:
            invoice_number = ''
        return invoice_number

    def _l10n_pe_cis_get_invoice_serie(self):
        invoice_number = self._l10n_pe_cis_get_invoice_number()
        invoice_serie = invoice_number[0] if invoice_number else ''
        return invoice_serie

    def _l10n_pe_cis_get_invoice_correlative_number(self):
        invoice_number = self._l10n_pe_cis_get_invoice_number()
        invoice_correlative = invoice_number[1] if invoice_number else ''
        invoice_correlative_is_number = bool(re.match(r'^\d+$', invoice_correlative))
        invoice_correlative_number = str(int(invoice_correlative)) if invoice_correlative_is_number else ''
        return invoice_correlative_number

    def _l10n_pe_cis_get_invoice_vat_number(self):
        if self.move_type in ['out_invoice', 'out_refund']:
            vat_number = self.company_id.vat if self.company_id and self.company_id.vat else ''
        elif self.move_type in ['in_invoice', 'in_refund']:
            vat_number = self.partner_id.vat if self.partner_id and self.partner_id.vat else ''
        else:
            vat_number = ''
        return vat_number

    def _l10n_pe_cis_get_invoice_data_values(self):
        invoice_serie = self._l10n_pe_cis_get_invoice_serie()
        invoice_data_values = {
            'numRuc': '{:.11}'.format(self._l10n_pe_cis_get_invoice_vat_number()),
            'codComp': '{:.2}'.format(self.l10n_latam_document_type_id.code),
            'numeroSerie': '{:.4}'.format(invoice_serie),
            'numero': '{:.8}'.format(self._l10n_pe_cis_get_invoice_correlative_number()),
            'fechaEmision': self.invoice_date.strftime('%d/%m/%Y'),
        }
        if invoice_serie and not invoice_serie[0].isdigit():
            invoice_data_values.update({'monto': '{:.2f}'.format(self.amount_total)})
        return invoice_data_values
        
    def _l10n_pe_cis_get_invoice_data(self):
        self._l10n_pe_cis_validate_invoice_data()
        invoice_data_values = self._l10n_pe_cis_get_invoice_data_values()
        invoice_data = {
            'numRuc': invoice_data_values['numRuc'],
            'codComp': invoice_data_values['codComp'],
            'numeroSerie': invoice_data_values['numeroSerie'],
            'numero': invoice_data_values['numero'],
            'fechaEmision': invoice_data_values['fechaEmision']
        }
        if 'monto' in invoice_data_values:
            invoice_data['monto'] = invoice_data_values['monto']
        return invoice_data

    def _l10n_pe_cis_get_response_data(self, token, company):
        url = 'https://api.sunat.gob.pe/v1/contribuyente/contribuyentes/{}/validarcomprobante'.format(company.vat)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(token)
        }
        invoice_data = json.dumps(self._l10n_pe_cis_get_invoice_data(), ensure_ascii=False)
        try:
            sunat_client = requests.post(url, data=invoice_data, headers=headers)
            response_data = json.loads(sunat_client.text)
            return response_data
        except requests.HTTPError:
            raise ValidationError('Error al establece la conexión.')
        except json.decoder.JSONDecodeError:
            raise ValidationError('Error en la obtención de datos. Intente de nuevo.')

    def action_query_integrated_cpe_sunat(self):
        company = self.company_id
        credentials = self._l10n_pe_cis_get_credentials(company)
        token = self._l10n_pe_cis_get_token(credentials)
        response_data = self._l10n_pe_cis_get_response_data(token, company)
             
        self.write({
            'l10n_pe_cis_cpe_status': response_data['data'].get('estadoCp', False)\
                if 'data' in response_data and 'estadoCp' in response_data['data'] else False,
            'l10n_pe_cis_taxpayer_status': response_data['data'].get('estadoRuc', False)\
                if 'data' in response_data and 'estadoRuc' in response_data['data'] else False,
            'l10n_pe_cis_taxpayer_domiciliary_status': response_data['data'].get('condDomiRuc', False)\
                if 'data' in response_data and 'condDomiRuc' in response_data['data'] else False,
            'l10n_pe_cis_state': 'exception' if response_data.get('errorCode') else 'confirmed',
            'l10n_pe_cis_query_status': response_data.get('success', False),
        })
        
        response_data_error_code = response_data.get('errorCode', False)
        response_data_message = response_data.get('message', False)
        response_data_observations = '\n<br>'.join(response_data['data']['observaciones'])\
            if 'data' in response_data and 'observaciones' in response_data['data'] else False
        message = (
            "<b>Consulta Integrada Generada:</b> <a href=# data-oe-model=account.move data-oe-id={}></a><br>"
            "<b>- Usuario:</b> {}<br>"
            "<b>- Fecha:</b> {}"
            "{}"
            "{}"
            "{}"
        ).format(
            self.id,
            self.env.user.name,
            self._l10n_pe_cis_convert_date_timezone(fields.Datetime.now()),
            "<br><b>- Código de error:</b> " + response_data_error_code if response_data_error_code else '',
            "<br><b>- Mensaje:</b> " + response_data_message if response_data_message else '',
            "<br><b>- Observaciones:</b><br> " + response_data_observations if response_data_observations else ''
        )
        self.message_post(body=message.strip())

    def _l10n_pe_cis_convert_date_timezone(self, date, format_time='%Y-%m-%d %H:%M:%S'):
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        if date:
            date_tz = pytz.utc.localize(date).astimezone(tz)
            date = date_tz.strftime(format_time)
        return date

    @api.model
    def _cron_execute_query_integrated_cpe_sunat(self, job_count=1):
        move_state = ['posted', 'cancel']
        move_types = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
        document_types = ['01','03','07','08']
        
        moves_to_process = self.search(
            [
                '|',
                ('l10n_pe_cis_state', '=', 'for_confirmed'),
                ('l10n_pe_cis_query_status', '=', False),
                ('state', 'in', move_state),
                ('move_type', 'in', move_types),
                ('invoice_date', '!=', False),
                ('l10n_latam_document_type_id', '!=', False),
                ('l10n_latam_document_type_id.code', 'in', document_types),
            ],
            order='create_date desc'
        )
        for move in moves_to_process[:job_count]:
            try:
                    move.action_query_integrated_cpe_sunat()
            except:
                pass
