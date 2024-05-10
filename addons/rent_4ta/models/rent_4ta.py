from odoo import fields, models
from odoo.exceptions import ValidationError

import base64
import json

from datetime import date, datetime

from ..reports.report_rent_4ta import ReportRent4ta



class Rent4taFiles(models.Model):
    _name = 'rent.4ta.files'
    _description = 'Rent 4ta Files'
    
    date_from = fields.Date(string='Fecha de Inicio', required=True)
    date_to = fields.Date(string='Fecha de Fin', required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )
    ps4_filename = fields.Char(string='Nombre archivo .ps4')
    ps4_binary = fields.Binary(string='.Ps4')
    quarter_filename = fields.Char(string='Nombre archivo .4ta')
    quarter_binary = fields.Binary(string='.4ta')
    error_dialog = fields.Text(readonly=True)

    def name_get(self):
        res = []
        for record in self:
            name = "%s - %s" % (record.date_from, record.date_to)
            res.append((record.id, name))
        return res
    
    def action_generate_files(self):
        self.update({
            'ps4_binary': None,
            'ps4_filename': None,
            'quarter_binary': None,
            'quarter_filename': None,
            'error_dialog': None
        })
        self.action_generate_rent_4ta_files()

    def action_generate_rent_4ta_files(self):
        data_ps4, data_4ta = self.generate_data_report_rent_4ta()
        if data_ps4 == {} or data_4ta == []:
            error_dialog = ""
            if data_ps4 == {}:
                error_dialog = "No hay contenido para generar el archivo .ps4 en este rango de fecha para esta compañia"
            if data_4ta == []:
                error_dialog = error_dialog + '\n%s' % ("No hay contenido para generar el archivo .4ta en este rango de fecha para esta compañia")
            self.write({'error_dialog': error_dialog})
        if data_ps4 == {} and data_4ta == []:
            return True
        report_ps4 = ReportRent4ta(self, data_ps4, data_4ta)
        values_content_ps4 = report_ps4.get_content_data_ps4()
        values_content_4ta = report_ps4.get_content_data_4ta()
        self.ps4_binary = base64.b64encode(values_content_ps4.encode() or '\n'.encode())
        self.quarter_binary = base64.b64encode(values_content_4ta.encode() or '\n'.encode())
        self.ps4_filename = report_ps4.get_filename('ps4')
        self.quarter_filename = report_ps4.get_filename('4ta')

    def search_data_report_rent_4ta(self):
        l10n_latam_document_type = self.env['l10n_latam.document.type'].search([
            ('code', '=', '02'),
            ('internal_type', '!=', False)
        ])
        
        if not any(l10n_latam_document_type):
            raise ValidationError("No se tiene configurado un tipo de documento con código 02 'Recibo por honorarios'")
        
        account_move_ids_list = []
        account_move_ids = self.env['account.move'].search([
            ('l10n_latam_document_type_id', '=', l10n_latam_document_type[0].id),
            ('state', '=', 'posted'),
            ('partner_id', '!=', False),
            ('company_id', '=', self.company_id.id)
        ])
        
        for move_id in account_move_ids:
            if move_id.invoice_payments_widget and (move_id.invoice_payments_widget != {} or move_id.invoice_payments_widget != []):
                invoice_payments_widget = move_id.invoice_payments_widget
                if type(invoice_payments_widget) != dict:
                    invoice_payments_widget = json.loads(move_id.invoice_payments_widget)
                if not isinstance(invoice_payments_widget['content'][0]['date'], date):
                    date_payment = datetime.strptime(invoice_payments_widget['content'][0]['date'], '%Y-%m-%d').date()
                else:
                    date_payment = invoice_payments_widget['content'][0]['date']
                if self.date_from <= date_payment and date_payment <= self.date_to:
                    account_move_ids_list.append(move_id)
                    
        return account_move_ids_list
        
    def generate_data_report_rent_4ta(self):
        data_ps4 = dict()
        data_4ta = list()

        account_move_ids_list = self.search_data_report_rent_4ta()
        
        for move_id in account_move_ids_list:
            if move_id.partner_id.vat:
                data_ps4[move_id.partner_id.vat] = []
        for line_data in data_ps4:
            for move_id in account_move_ids_list:
                if line_data == move_id.partner_id.vat:
                    document_type_code = move_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code
                    if len(document_type_code) == 1:
                        document_type_code = "0%s" % (document_type_code)
                    lines = {
                        'document_type_code': document_type_code[:2] if document_type_code else '',
                        'document_number': move_id.partner_id.vat[:11] if move_id.partner_id.vat else '',
                        'first_name': move_id.partner_id.first_name if move_id.partner_id.first_name else '',
                        'second_name': move_id.partner_id.second_name if move_id.partner_id.second_name else '',
                        'partner_name': move_id.partner_id.partner_name if move_id.partner_id.partner_name else '',
                        'is_nodomicilied': '2' if move_id.is_nodomicilied else '1',
                        'double_taxation_code': move_id.partner_id.double_taxation if move_id.partner_id.double_taxation else '0'
                        }
                    data_ps4[move_id.partner_id.vat].append(lines)
        
        for move_id in account_move_ids_list:
            document_type_code = move_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code
            quarter = '0'
            if len(document_type_code) == 1:
                document_type_code = "0%s" % (document_type_code)
            if move_id.tax_totals_json:
                if json.loads(move_id.tax_totals_json)['groups_by_subtotal']:
                    for line in json.loads(move_id.tax_totals_json)['groups_by_subtotal']['Untaxed Amount']:
                        if line['tax_group_name'] in ['4TA', 'RTA'] and abs(line['tax_group_amount']) > 0:
                            quarter = '1'
            date_payment = ''
            if move_id.invoice_payments_widget:
                invoice_payments_widget = move_id.invoice_payments_widget
                if type(invoice_payments_widget) != dict:
                    invoice_payments_widget = json.loads(move_id.invoice_payments_widget)
                if not isinstance(invoice_payments_widget['content'][0]['date'], date):
                    date_payment = datetime.strptime(invoice_payments_widget['content'][0]['date'], '%Y-%m-%d')
                else:
                    date_payment = invoice_payments_widget['content'][0]['date']
                date_payment =  date.strftime(date_payment, '%d/%m/%Y')
            lines = {
                'document_type_code': document_type_code[:2] if document_type_code else '',
                'document_number': move_id.partner_id.vat[:11] if move_id.partner_id.vat else '',
                'ref_prefix': ''.join(move_id.ref[char] for char in range(0, move_id.ref.find('-'))) if move_id.ref and move_id.ref.find('-') != -1 else '',
                'ref_suffix': ''.join(move_id.ref[char] for char in range(move_id.ref.find('-') + 1, len(move_id.ref))) if move_id.ref and move_id.ref.find('-') != -1 else '',
                'amount_total': '{:.2f}'.format(json.loads(move_id.tax_totals_json)['amount_untaxed']) if move_id.tax_totals_json else '',
                'invoice_date': date.strftime(move_id.invoice_date, '%d/%m/%Y') if move_id.invoice_date else '',
                'payment_date': date_payment,
                'quarter': quarter
            }
            data_4ta.append(lines)
        
        return data_ps4, data_4ta
