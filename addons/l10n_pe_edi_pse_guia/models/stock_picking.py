# -*- coding: utf-8 -*-
import base64
import logging
import re
import requests
import json
from odoo import api, models, fields, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_round, html_escape
from requests.exceptions import ConnectionError, HTTPError, InvalidSchema, InvalidURL, ReadTimeout

log = logging.getLogger(__name__)

DEFAULT_CONFLUX_GUIA_ENDPOINT = 'https://einvoice.conflux.pe/api/v/1/account_einvoice/despatch/'
DEFAULT_CONFLUX_GUIA_ESTADO_ENDPOINT = 'https://einvoice.conflux.pe/api/v/1/account_einvoice/despatch/%s/status/'

def request_json(token="", method="post", url=None, data_dict=None):
    s = requests.Session()
    if not url:
        raise InvalidURL(_("Url not provided"))
    try:
        if method=='post':
            r = s.post(
                url,
                headers={'Authorization': 'Token '+token},
                json=data_dict)
        else:
            r = s.get(
                url,
                headers={'Authorization': 'Token '+token},
                json=data_dict)
    except requests.exceptions.RequestException as e:
        return {"message":_("Exception: %s" % e)}
    if r.status_code in (200,400):
        try:
            response = json.loads(r.content.decode())
            log.info(response)
        except ValueError as e:
            return {"message":_("Exception decoding JSON response: %s" % e)}

        return response
    else:
        log.info(url)
        log.info(token)
        log.info(data_dict)
        log.info(r.status_code)
        log.info(r.content)
        return {"message":_("There's problems to connect with PSE Server")}


class Picking(models.Model):
    _inherit = 'stock.picking'

    l10n_pe_edi_sequence_id = fields.Many2one('ir.sequence', string='Serial Sequence', domain=[('code','=','l10n_pe_edi_stock.stock_picking_sunat_sequence')])
    l10n_pe_edi_pse_uid = fields.Char(string='PSE Unique identifier', copy=False)
    l10n_pe_edi_qr_text = fields.Char(string='QR Text', copy=False)
    l10n_pe_edi_accepted_by_sunat = fields.Boolean(string='EDI Accepted by Sunat', copy=False)

    def action_send_delivery_guide_pse(self):
        """Make the validations required to generate the EDI document, generates the XML, and sent to sign in the
        SUNAT"""
        self._check_company()
        self._l10n_pe_edi_check_required_data()
        for record in self:
            provider = record.company_id.l10n_pe_edi_provider
            if not record.l10n_latam_document_number and record.l10n_pe_edi_sequence_id:
                record.l10n_latam_document_number = record.l10n_pe_edi_sequence_id.next_by_id()
            if not record.l10n_latam_document_number and not record.l10n_pe_edi_sequence_id:
                sunat_sequence = self.env['ir.sequence'].search([
                    ('code', '=', 'l10n_pe_edi_stock.stock_picking_sunat_sequence'),
                    ('company_id', '=', record.company_id.id)], limit=1)
                if not sunat_sequence:
                    sunat_sequence = self.env['ir.sequence'].sudo().create({
                        'name': 'Stock Picking Sunat Sequence %s' % record.company_id.name,
                        'code': 'l10n_pe_edi_stock.stock_picking_sunat_sequence',
                        'padding': 8,
                        'company_id': record.company_id.id,
                        'prefix': 'T001-',
                        'number_next': 1,
                    })
                record.l10n_pe_edi_sequence_id = sunat_sequence
                record.l10n_latam_document_number = sunat_sequence.next_by_id()
            edi_filename = '%s-09-%s' % (
                record.company_id.vat,
                (record.l10n_latam_document_number or '').replace(' ', ''),
            )
            res = getattr(record, '_l10n_pe_edi_sign_delivery_%s' % provider)(record)

            if 'error' in res:
                record.l10n_pe_edi_error = res['error']
                continue

            # == Create the attachments ==
            if res.get('xml_document'):
                record._l10n_pe_edi_decode_cdr(edi_filename, res['xml_document'])
            if res.get('cdr'):
                res_attachment = self.env['ir.attachment'].create({
                    'res_model': record._name,
                    'res_id': record.id,
                    'type': 'binary',
                    'name': 'cdr-%s.xml' % edi_filename,
                    'raw': res['cdr'],
                    'mimetype': 'application/xml',
                })
            else:
                continue
            message = _("The EDI document was successfully created and signed by the government.")
            record._message_log(body=message, attachment_ids=res_attachment.ids)
            record.write({'l10n_pe_edi_error': False, 'l10n_pe_edi_status': 'sent'})
    
    def _l10n_pe_edi_get_edi_values_conflux(self, picking):
        base_dte = self._l10n_pe_edi_get_delivery_guide_values()
        record = base_dte.get('record')

        invoice_sequence = picking.l10n_latam_document_number.split('-')
        
        dte_serial = ''
        dte_number = ''
        if len(invoice_sequence)==2:
            dte_serial = invoice_sequence[0]
            dte_number = invoice_sequence[1]

        origin_address_id = base_dte.get('warehouse_address')
        delivery_address_id = picking.partner_id
        _despatch = {
            'enviar': True,
            'serie': dte_serial,
            'numero': dte_number,
            'nombre_de_archivo': '%s-09-%s' % (picking.company_id.vat,record.l10n_latam_document_number),
            'motivo_de_envio': picking.l10n_pe_edi_reason_for_transfer,
            'modo_de_transporte': picking.l10n_pe_edi_transport_type,
            'tipo_de_guia': '09',
            'informacion_de_envio': picking.l10n_pe_edi_reason_for_transfer,

            'receptor_denominacion': picking.partner_id.name,
            'receptor_tipo_de_documento': picking.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            'receptor_numero_de_documento': picking.partner_id.vat,
            'receptor_direccion': picking.partner_id.street,

            'fecha_de_emision': base_dte.get('date_issue'),
            'fecha_de_inicio': picking.l10n_pe_edi_departure_start_date.strftime("%Y-%m-%d"),

            'peso': picking.weight,
            'bultos_paquetes':0,
            'unidad_de_medida_peso': 'KGM',

            'origen_establecimiento_anexo': origin_address_id.l10n_pe_edi_address_type_code or None,
            'origen_ubigeo': origin_address_id.l10n_pe_district.code if origin_address_id.l10n_pe_district else False,
            'origen_direccion': (origin_address_id.street_name or '') \
                                + (origin_address_id.street_number and (' ' + origin_address_id.street_number) or '') \
                                + (origin_address_id.street_number2 and (' ' + origin_address_id.street_number2) or '') \
                                + (origin_address_id.street2 and (' ' + origin_address_id.street2) or '') \
                                + (origin_address_id.l10n_pe_district and ', ' + origin_address_id.l10n_pe_district.name or '') \
                                + (origin_address_id.city_id and ', ' + origin_address_id.city_id.name or '') \
                                + (origin_address_id.state_id and ', ' + origin_address_id.state_id.name or '') \
                                + (origin_address_id.country_id and ', ' + origin_address_id.country_id.name or ''),
            'destino_establecimiento_anexo': delivery_address_id.l10n_pe_edi_address_type_code or None,
            'destino_ubigeo': delivery_address_id.l10n_pe_district.code if delivery_address_id.l10n_pe_district else False,
            'destino_direccion': (delivery_address_id.street_name or '') \
                                + (delivery_address_id.street_number and (' ' + delivery_address_id.street_number) or '') \
                                + (delivery_address_id.street_number2 and (' ' + delivery_address_id.street_number2) or '') \
                                + (delivery_address_id.street2 and (' ' + delivery_address_id.street2) or '') \
                                + (delivery_address_id.l10n_pe_district and ', ' + delivery_address_id.l10n_pe_district.name or '') \
                                + (delivery_address_id.city_id and ', ' + delivery_address_id.city_id.name or '') \
                                + (delivery_address_id.state_id and ', ' + delivery_address_id.state_id.name or '') \
                                + (delivery_address_id.country_id and ', ' + delivery_address_id.country_id.name or ''),
            'traslado_con_vehiculo_m1_l': picking.l10n_pe_edi_vehicle_id.is_m1l,
            'items': []
        }

        if picking.l10n_pe_edi_observation:
            if picking.l10n_pe_edi_observation!='':
                _despatch['observaciones'] = picking.l10n_pe_edi_observation

        if picking.l10n_pe_edi_vehicle_id:
            _despatch.update({
                'placa_de_vehiculo': picking.l10n_pe_edi_vehicle_id.license_plate,
            })

        if picking.l10n_pe_edi_transport_type=='01':
            if picking.l10n_pe_edi_operator_id:
                _despatch.update({
                    'portador_denominacion': picking.l10n_pe_edi_operator_id.name,
                    'portador_tipo_de_documento': picking.l10n_pe_edi_operator_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
                    'portador_numero_de_documento': picking.l10n_pe_edi_operator_id.vat,
                    'portador_registro_mtc': picking.l10n_pe_edi_operator_id.l10n_pe_edi_mtc_number or None,
                })
        if picking.l10n_pe_edi_transport_type=='02':
            if picking.l10n_pe_edi_transport_type:
                _despatch.update({
                    'operador_denominacion': picking.l10n_pe_edi_operator_id.name,
                    'operador_tipo_de_documento': picking.l10n_pe_edi_operator_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
                    'operador_numero_de_documeto': picking.l10n_pe_edi_operator_id.vat,
                    'operador_licencia': picking.l10n_pe_edi_operator_id.l10n_pe_edi_operator_license or None,
                })

        if picking.l10n_pe_edi_document_number and picking.l10n_pe_edi_related_document_type:
            _despatch['documentos_de_referencia'] = [{
                'numero_de_documento': picking.l10n_pe_edi_document_number,
                'tipo_de_documento': picking.l10n_pe_edi_related_document_type,
                'proveedor_documento_tipo': picking.company_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code if picking.l10n_pe_edi_related_document_type in ('01', '03', '04', '09', '12', '48') else None,
                'proveedor_documento_numero': picking.company_id.vat if picking.l10n_pe_edi_related_document_type in ('01', '03', '04', '09', '12', '48') else None,
            }]

        if base_dte.get('moves'):
            for move in base_dte.get('moves'):
                _item = {
                    'cantidad': move.quantity_done,
                    'descripcion': move.description_picking if move.description_picking else move.product_id.name,
                    'codigo': move.product_id.default_code or '',
                    'codigo_producto_sunat': move.product_id.unspsc_code_id.code or '',
                    'unidad_de_medida': move.product_uom.l10n_pe_edi_measure_unit_code or 'NIU',
                    'unidad_de_medida_peso': 'KGM'
                }
                _despatch['items'].append(_item)
        return _despatch

    def _l10n_pe_edi_sign_service_step_2_conflux(self, company, uid_despatch):
        try:
            result = request_json(url=DEFAULT_CONFLUX_GUIA_ESTADO_ENDPOINT % uid_despatch, method='get', token=company.l10n_pe_edi_pse_secret_key, data_dict={})
        except InvalidSchema:
            return {'error': self._l10n_pe_edi_get_general_error_messages()['L10NPE16'], 'blocking_level': 'error'}
        except AccessError:
            return {'error': self._l10n_pe_edi_get_general_error_messages()['L10NPE17'], 'blocking_level': 'warning'}
        except InvalidURL:
            return {'error': self._l10n_pe_edi_get_general_error_messages()['L10NPE18'], 'blocking_level': 'error'}

        if result.get('message') and result.get('status')=='error':
            if result['message'] == 'no-credit':
                error_message = self._l10n_pe_edi_get_iap_buy_credits_message(company)
            else:
                error_message = 'Error al consultar estado de documento: %s' % result['message']
            return {'error': error_message, 'blocking_level': 'error'}

        xml_document = None
        cdr = None
        pdf_url = None
        ticket_code = None

        if result.get('sunat_ticket', False):
            ticket_code = result['sunat_ticket']
    
        if result.get('emision_aceptada', False):
            if result.get('enlace_del_cdr', False):
                r_cdr = requests.get(result['enlace_del_cdr'])
                cdr = r_cdr.content
            if result.get('enlace_del_xml', False):
                r_xml = requests.get(result['enlace_del_xml'])
                xml_document = r_xml.content

            return {
                'xml_document':xml_document,
                'pdf':pdf_url,
                'cdr':cdr,
                'edi_accepted':True,
                'qr': result.get('cadena_para_codigo_qr'),
                'ticket_code':ticket_code,
            }
        if result.get('emision_rechazada', False):
            return {
                'ticket_code':ticket_code,
                'error': '%s - %s' % (result.get('sunat_description', ''), result.get('sunat_note', '')),
                'extra_msg': '%s - %s' % (result.get('sunat_description', ''), result.get('sunat_note', '')), 
                'blocking_level': 'error'
            }
        extra_msg = ''
        return {'xml_document': xml_document, 'cdr': cdr, 'ticket_code': ticket_code, 'extra_msg': extra_msg}

    def _l10n_pe_edi_sign_service_step_1_conflux(self, company, data_dict, latam_document_type, serie_folio):
        try:
            result = request_json(url=DEFAULT_CONFLUX_GUIA_ENDPOINT, method='post', token=company.l10n_pe_edi_pse_secret_key, data_dict=data_dict)
        except InvalidSchema:
            return {'error': self._l10n_pe_edi_get_general_error_messages()['L10NPE16'], 'blocking_level': 'error'}
        except AccessError:
            return {'error': self._l10n_pe_edi_get_general_error_messages()['L10NPE17'], 'blocking_level': 'warning'}
        except InvalidURL:
            return {'error': self._l10n_pe_edi_get_general_error_messages()['L10NPE18'], 'blocking_level': 'error'}

        if result.get('message') and result.get('status')=='error':
            if result['message'] == 'no-credit':
                error_message = self._l10n_pe_edi_get_iap_buy_credits_message(company)
            else:
                error_message = result['message']
            return {'error': error_message, 'blocking_level': 'error'}

        xml_document = None
        cdr = None
        pdf_url = None
        
        if result.get('status')=='success':
            if result['success']['data'].get('emision_aceptada', False):
                if result['success']['data'].get('enlace_del_cdr', False):
                    r_cdr = requests.get(result['success']['data']['enlace_del_cdr'])
                    cdr = r_cdr.content
                if result['success']['data'].get('enlace_del_xml', False):
                    r_xml = requests.get(result['success']['data']['enlace_del_xml'])
                    xml_document = r_xml.content
                return {
                    'uid':result['success']['data']['uid'],
                    'xml_document':xml_document,
                    'pdf':pdf_url,
                    'cdr':cdr,
                    'edi_accepted': True,
                    'qr': result.get('cadena_para_codigo_qr')
                }
            else:
                xml_url = ''
                if result['success']['data'].get('enlace_del_xml', False):
                    xml_url = '<a href="%s" target="_blank">%s</a>' % (result['success']['data']['enlace_del_xml'],result['success']['data']['enlace_del_xml'])
                pdf_url = ''
                if result['success']['data'].get('enlace_del_pdf', False):
                    pdf_url = '<a href="%s" target="_blank">%s</a>' % (result['success']['data']['enlace_del_pdf'],result['success']['data']['enlace_del_pdf'])
                return {
                    'uid':result['success']['data']['uid'],
                    'error': _("Validation is in progress in the government side (identifier: %s).", html_escape(result['success']['data']['uid'])),
                    'blocking_level': 'info',
                    'extra_msg':_("The EDI document was successfully created and signed by the PSE.<br/>" +
                                "XML download link: %s<br/>"
                                "PDF download link: %s" % (xml_url, pdf_url))
                }
        extra_msg = result.get('message','')
        return {'xml_document': xml_document, 'cdr': cdr, 'extra_msg': extra_msg}

    def _l10n_pe_edi_get_qr(self):
        #OVERRIDE
        self.ensure_one()
        return self.l10n_pe_edi_qr_text or ''

    def _l10n_pe_edi_sign_delivery_conflux(self, picking):
        if(picking.l10n_pe_edi_pse_uid):
            service_iap = self._l10n_pe_edi_sign_service_step_2_conflux(
                picking.company_id, picking.l10n_pe_edi_pse_uid)
        else:
            edi_conflux_values = self._l10n_pe_edi_get_edi_values_conflux(picking)
            service_iap = self._l10n_pe_edi_sign_service_step_1_conflux(
                picking.company_id, edi_conflux_values, '09',
                picking._l10n_pe_edi_get_serie_folio())
        if service_iap.get('extra_msg'):
            picking.message_post(body=service_iap['extra_msg'])
        update_picking = {}
        if service_iap.get('edi_accepted', False):
            update_picking['l10n_pe_edi_accepted_by_sunat'] = service_iap.get('edi_accepted')
        if service_iap.get('uid', False):
            update_picking['l10n_pe_edi_pse_uid'] = service_iap.get('uid')
        if service_iap.get('qr', False):
            update_picking['l10n_pe_edi_qr_text'] = service_iap.get('qr')
        if service_iap.get('ticket_code', False):
            update_picking['l10n_pe_edi_ticket_number'] = service_iap.get('ticket_code')
        if update_picking:
            picking.write(update_picking)
        return service_iap