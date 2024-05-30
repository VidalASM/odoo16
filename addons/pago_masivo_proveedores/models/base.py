from odoo import api, fields, models
from ..reports.report_detractions import ReportInvBalTxt
from datetime import datetime
import base64
import json
import pytz

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    bank_id_related = fields.Selection(string='Bank relation code', related='bank_id.sunat_bank_code')
    company_code = fields.Char(string="Código de la empresa")
    service_code = fields.Char(string="Código del servicio")
    account_type = fields.Selection(string='Tipo de cuenta', selection=[
        ('001', 'Cuenta Corriente'),
        ('002', 'Cuenta de Ahorros'),
    ])


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_type = fields.Selection(string='Tipo de cuenta', selection=[
        ('001', 'Corriente'),
        ('002', 'Ahorro'),
        ('003', 'Detracción'),
    ])


class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'

    process_type = fields.Selection(string='Tipo de proceso', selection=[
        ('A', 'Inmediato'),
        ('F', 'Fecha futura'),
        ('H', 'Horario de ejecución'),
    ])
    future_date = fields.Date(string='Fecha futura')
    executing_schedule = fields.Selection(string='Horario de ejecución', selection=[
        ('B', '11:00 horas'),
        ('C', '15:00 horas'),
        ('D', '19:00 horas'),
    ])
    validate_belonging = fields.Boolean(string='Validar pertenencia')
    journal_temporal_code = fields.Selection(related='journal_id.bank_id_related')
    process_type_itb = fields.Selection(string='Tipo de proceso', selection=[
        ('0', 'En línea'),
        ('1', 'En diferdo'),
    ])
    future_date_itb = fields.Date(string='Fecha futura')
    count_txt = fields.Integer(string='Contador', default=0)

    txt_filename_bank = fields.Char(string='Filaname_bank .txt')
    txt_binary_bank = fields.Binary(string='Reporte_bank .TXT')

    txt_filename_scotia = fields.Char(string='Pago')
    txt_binary_scotia = fields.Binary(string='Pago .txt')
    txt_filename_scotia_zip = fields.Char(string='Pago .zip')
    txt_binary_scotia_zip = fields.Binary(string='Pago .zip')

    def generate_txt_suppliers(self):
        amount_total = 0
        lines = 0
        zeros = '00000000000000000000000000000000'
        type_bank = ' '
        line_data = []
        line_data_2 = []
        line_data_scot = []
        list_data = {}
        total_account = 0

        if self.journal_temporal_code == '11':
            type_bank = '11'
            for payment in self.payment_ids:
                amount_total = amount_total + payment.amount
                lines = lines + 1
                if payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'DNI':
                    code_doc = 'L'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'RUC':
                    code_doc = 'R'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Carnet Militar':
                    code_doc = 'M'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Cédula Extranjera':
                    code_doc = 'E'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Pasaporte':
                    code_doc = 'P'
                else:
                    code_doc = ' '

                if payment.partner_id.bank_ids:
                    for bank in payment.partner_id.bank_ids:
                        if bank.bank_id.sunat_bank_code == '11':
                            cod_bank = 'P'
                            account = str(bank.acc_number).ljust(20, ' ')
                            break
                        else:
                            if bank.account_type != '003':
                                cod_bank = 'I'
                                account = str(bank.cci).ljust(20, ' ')
                else:
                    cod_bank = 'I'
                    account = ' '.ljust(20, ' ')

                values = {
                    'name': code_doc,
                    'vat': str(payment.partner_id.vat).ljust(12, ' '),
                    'bank': cod_bank,
                    'account': account.ljust(20, ' '),
                    'name_client': str(payment.partner_id.name).ljust(40, ' '),
                    'amount': str(f"{payment.amount:.2f}").replace('.', '').rjust(15, '0'),
                    'document': payment.reconciled_bill_ids.l10n_latam_document_type_id.name[
                                :1] if payment.reconciled_bill_ids.l10n_latam_document_type_id.internal_type in ['invoice',
                                                                                                                 'credit_note'] else '',
                    'ref': str(payment.ref)[-8:].ljust(12, ' '),
                    'N': 'N',
                    'payment_name': str(payment.name).ljust(40, ' '),
                    'zeros': zeros.rjust(113, ' ') + ' ' * 18
                }
                line_data.append(values)
            list_data = {
                'bank_account_id': str(self.journal_id.bank_account_id.acc_number).ljust(20, ' '),
                'currency_id': 'PEN' if not self.journal_id.currency_id or self.journal_id.currency_id.name == 'PEN' else '   ',
                'amount_total': str(f"{amount_total:.2f}").replace('.', '').rjust(15, '0'),
                'process_type': self.process_type if self.process_type else ' ',
                'date': str(self.future_date).replace('-', '') if self.future_date else str(self.date).replace('-', ''),
                'executing_schedule': self.executing_schedule if self.executing_schedule else ' ',
                'reference': self.name.ljust(25, ' ') if self.name else ' '.ljust(25, ' '),
                'lines': str(lines).rjust(6, '0'),
                'validate_belonging': 'S' if self.validate_belonging else 'N',
                'zeros':'000000000000000000'.ljust(68, ' ')
            }
        elif self.journal_temporal_code == '02':
            type_bank = '02'
            for payment in self.payment_ids:
                amount_total = amount_total + payment.amount
                lines = lines + 1
                if payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'DNI':
                    code_doc = '1'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'RUC':
                    code_doc = '6'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'FIC':
                    code_doc = '7'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Cédula Extranjera':
                    code_doc = '3'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Pasaporte':
                    code_doc = '4'
                else:
                    code_doc = ' '

                if payment.partner_id.bank_ids:
                    for bank in payment.partner_id.bank_ids:
                        if bank.bank_id.sunat_bank_code == '02' and bank.account_type == '002':
                            bank_cod = 'A'
                            account = str(bank.acc_number).ljust(20, ' ')
                            break
                        elif bank.bank_id.sunat_bank_code == '02' and bank.account_type == '001':
                            bank_cod = 'C'
                            account = str(bank.acc_number).ljust(20, ' ')
                            break
                        else:
                            if bank.account_type != '003':
                                bank_cod = 'B'
                                account = str(bank.cci).ljust(20, ' ')
                else:
                    bank_cod = 'B'
                    account = ' '.ljust(20, ' ')

                if account != ' '.ljust(20, ' '):
                    total_account = total_account + int(account.replace('-', ''))

                payment_amount_str = str(payment.amount)
                if len(payment_amount_str.split('.')) < 2:
                    payment_amount_str += '.0'

                values = {
                    'id': '2',
                    'bank_cod': bank_cod,
                    'account': account,
                    'id_2': '1',
                    'doc': code_doc,
                    'vat': str(payment.partner_id.vat).ljust(12, ' '),
                    'spaces': '   ',
                    'ref': str(payment.partner_id.name[:75]).ljust(75, ' '),
                    'reference': str(self.name[:40]).ljust(40, ' '),
                    'currency': str(self.name[:40]) + ' ' + '0001' if payment.currency_id.name == 'PEN' or not payment.currency_id else '1001',
                    'amount': (payment_amount_str + '0').rjust(17, '0') if len(payment_amount_str.split('.')[1]) < 2 else str(round(payment.amount, 2)).rjust(17, '0'),
                    'N': 'S',
                }
                line_data.append(values)
                latam_document = self.env['account.move'].search([('name','=',payment.move_id.ref)])
                if latam_document and latam_document.l10n_latam_document_type_id.name == 'Factura':
                    doc = 'F'
                elif latam_document.l10n_latam_document_type_id.name == 'Nota crédito proveedor':
                    doc = 'N'
                elif latam_document.l10n_latam_document_type_id.name == 'Nota débito proveedor':
                    doc = 'C'
                elif latam_document.l10n_latam_document_type_id.name == 'Factura de la empresa':
                    doc = 'E'
                elif latam_document.l10n_latam_document_type_id.name == 'Nota crédito empresa':
                    doc = 'M'
                elif latam_document.l10n_latam_document_type_id.name == 'Nota débito empresa':
                    doc = 'B'
                elif latam_document.l10n_latam_document_type_id.name == 'Cobranza':
                    doc = 'Z'
                else:
                    doc = 'D'
                values = {
                    'id': '3',
                    'document': doc,
                    'ref': str(payment.ref).ljust(15, ' '),
                    'amount': (str(payment.amount) + '0').rjust(17, '0') if len(str(payment.amount).split('.')[1]) < 2 else str(round(payment.amount, 2)).rjust(17, '0'),
                }
                line_data_2.append(values)

            total_account = total_account + int((self.journal_id.bank_account_id.acc_number).replace('-', ''))
            amount_total_str = str(amount_total)
            if len(amount_total_str.split('.')) < 2:
                amount_total_str += '.0'
            list_data = {
                'id': '1',
                'lines_total': str(lines).rjust(6, '0'),
                'date': str(self.date).replace('-', '').replace(' ', '').replace(':', '') if self.date else '        ',
                'c': 'C',
                'currency': '0001' if self.journal_id.currency_id.name == 'PEN' or not self.journal_id.currency_id else '1001',
                'acc_number': str(self.journal_id.bank_account_id.acc_number).ljust(20, ' '),
                'amount_total': (amount_total_str + '0').rjust(17, '0') if len(amount_total_str.split('.')[1]) < 2 else str(round(amount_total, 2)).rjust(17, '0'),
                'reference': str(self.name).ljust(40, ' '),
                'N': 'N',
                'abono': str(total_account)[-15:].rjust(15, '0'),
            }
        elif self.journal_temporal_code == '03':
            self.count_txt = self.count_txt + 1
            type_bank = '03'
            for payment in self.payment_ids:
                amount_total = amount_total + payment.amount
                lines = lines + 1

                if payment.reconciled_bill_ids.l10n_latam_document_type_id.internal_type == 'invoice':
                    code_doc = 'F'
                elif payment.reconciled_bill_ids.l10n_latam_document_type_id.internal_type == 'credit_note':
                    code_doc = 'C'
                elif payment.reconciled_bill_ids.l10n_latam_document_type_id.internal_type == 'debit_note':
                    code_doc = 'D'
                else:
                    code_doc = ' '

                if payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'DNI':
                    doc_tyoe = '01'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'RUC':
                    doc_tyoe = '02'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Cédula Extranjera':
                    doc_tyoe = '03'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Pasaporte':
                    doc_tyoe = '05'
                else:
                    doc_tyoe = ' '

                if payment.partner_id.bank_ids:
                    for bank in payment.partner_id.bank_ids:
                        if bank.bank_id.sunat_bank_code == '03':
                            sunat_code = '09'
                            account_type = bank.account_type
                            account = str(bank.acc_number).ljust(20, ' ')
                            break
                        else:
                            if bank.account_type != '003':
                                sunat_code = '99'
                                account_type = bank.account_type
                                account = str(bank.cci).ljust(20, ' ')
                else:
                    sunat_code = '99'
                    account_type = '   '
                    account = ' '.ljust(20, ' ')

                values = {
                    'ruc': str(payment.partner_id.vat).ljust(20, ' ') if payment.partner_id.vat else ' '.ljust(20, ' '),
                    'doc': code_doc,
                    'payment': str(payment.move_id.payment_reference).ljust(20, ' ') if payment.move_id.payment_reference else ' '.ljust(20, ' '),
                    'currency': '01' if payment.currency_id.name == 'PEN' else '10',
                    'amount': str(f"{payment.amount:.2f}").replace('.', '').rjust(15, '0') if payment.amount else ' '.rjust(15, '0'),
                    'space': ' ',
                    'sunat_bank_code': sunat_code,
                    'account_type': account_type,
                    'currency_id': '01' if payment.currency_id.name == 'PEN' else '10',
                    'acc_3': account[0:3],
                    'account': account[:20],
                    'type_document': 'C' if payment.partner_id.l10n_latam_identification_type_id.name == 'RUC' else 'P',
                    'doc_tyoe': doc_tyoe,
                    'document': str(payment.partner_id.vat).ljust(15, ' ') if payment.partner_id.vat else ' '.ljust(15, ' '),
                    'name': str(payment.partner_id.name).ljust(60, ' ') if payment.partner_id.name else ' '.ljust(60, ' '),
                    '203': ' ' * 203,
                }
                line_data.append(values)

            amount_total_str = str(amount_total)
            if len(amount_total_str.split('.')) < 2:
                amount_total_str += '.0'
            amount_total = amount_total_str + '0' if len(amount_total_str.split('.')[1]) < 2 else str(round(amount_total, 2))

            timezone = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            formatted_date_time = datetime.now()
            if timezone != 'UTC':
                formatted_date_time = datetime.now().astimezone(timezone)

            list_data = {
                'company_code': self.journal_id.company_code,
                'service_code': self.journal_id.service_code,
                'bank_account': self.journal_id.bank_account_id.acc_number.ljust(13, ' '),
                'account_type': self.journal_id.account_type,
                'currency_id': '01' if self.journal_id.currency_id.name == 'PEN' or not self.journal_id.currency_id else '10',
                'pay': 'Pagos a prov',
                'date_time': str(formatted_date_time).split('.')[0].replace('-', '').replace(' ', '').replace(':', ''),
                'process_type_itb': self.process_type_itb,
                'date': datetime.today().strftime('%Y%m%d') if self.process_type_itb == '0' else str(self.future_date_itb).replace('-', ''),
                'lines': str(lines).rjust(6, '0'),
                'amount_total_pen': str(amount_total).replace(',', '').replace('.', '').rjust(15,
                                                                                              '0') if (self.journal_id.currency_id and self.journal_id.currency_id.name == 'PEN') or not self.journal_id.currency_id else '000000000000000',
                'amount_total_usd': str(amount_total).replace(',', '').replace('.', '').rjust(15,
                                                                                              '0') if self.journal_id.currency_id and self.journal_id.currency_id.name == 'USD' else '000000000000000',
                'm': 'MC001',
            }
        elif self.journal_temporal_code == '09':
            type_bank = '09'
            for payment in self.payment_ids:
                type_acc = ' '
                acc_number = '            '
                cci_number = '            '
                cci_to_scot = False
                acc_to_scot = False
                for bank in payment.partner_id.bank_ids:
                    if not cci_to_scot:
                        cci_number = str(bank.cci).ljust(20, ' ')
                    if not acc_to_scot and bank.bank_id.sunat_bank_code == '09':
                        acc_to_scot = str(bank.acc_number).ljust(20, ' ')
                    if bank.bank_id.sunat_bank_code == '09' and bank.account_type == '002':
                        type_acc = '3'
                        acc_number = str(bank.acc_number).ljust(20, ' ')
                    elif bank.bank_id.sunat_bank_code == '09' and bank.account_type == '001':
                        type_acc = '2'
                        acc_number = str(bank.acc_number).ljust(20, ' ')
                    elif bank.bank_id.sunat_bank_code != '09' and bank.account_type != '003' and type_acc == ' ':
                        type_acc = '4'
                        cci_number = str(bank.cci).ljust(20, ' ')
                    else:
                        continue

                count_account = 0
                batch_partner = payment.partner_id
                for batch in self.payment_ids:
                    if batch.partner_id == batch_partner:
                        count_account = count_account + 1

                values = {
                    'ruc': str(payment.partner_id.vat).ljust(11, ' ') if payment.partner_id.vat else ' '.ljust(11, ' '),
                    'name': str(payment.partner_id.name).ljust(60, ' ') if payment.partner_id.name else ' '.ljust(60, ' '),
                    'ref': str(payment.ref).rjust(14, '0'),
                    'invoice_date': payment.reconciled_bill_ids.invoice_date.strftime('%Y%m%d'),
                    'type_acc': type_acc,
                    'acc_number': acc_number,
                    'count_account': 'N' if count_account > 1 else 'S',
                    'cci_number': cci_number,
                    'space': ' ' * 50,
                    'currency_id': '01' if payment.currency_id.name == 'USD' else '00',
                }
                line_data.append(values)

                if payment.currency_id.name == 'PEN':
                    amount_payment_line = payment.amount
                else:
                    currency_payment = self.env['res.currency'].search([('name', '=', 'USD'), ('active', '=', True)])
                    amount_payment_line = payment.amount / currency_payment.rate

                values_scot = {
                    'ruc': str(payment.partner_id.vat).ljust(11, ' ') if payment.partner_id.vat else ' '.ljust(11, ' '),
                    'name': str(payment.partner_id.name).ljust(60, ' ') if payment.partner_id.name else ' '.ljust(60, ' '),
                    'email': str(self.env.company.email).ljust(60, ' ') if self.env.company.email else ' '.ljust(60, ' '),
                    'ref': str(payment.ref).ljust(19, ' ') if len(str(payment.ref)) < 19 else str(payment.ref)[:19],
                    'currency_id': '0' if not self.journal_id.currency_id or self.journal_id.currency_id.name == 'PEN' else '1',
                    'amount': str(f"{payment.amount:.2f}").replace('.', '').rjust(15, '0') if payment.amount else ' '.rjust(15, '0'),
                    'spaces': '               ',
                    'bank': acc_to_scot if acc_to_scot else cci_to_scot,
                }
                line_data_scot.append(values_scot)
        else:
            return

        data_name = {
            'name': self.name
        }

        if self.journal_temporal_code == '03':
            timezone = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            formatted_date_time = datetime.now()
            if timezone != 'UTC':
                formatted_date_time = datetime.now().astimezone(timezone)

            data_name = {
                'company_code': self.journal_id.company_code,
                'service_code': self.journal_id.service_code,
                'count_txt': str(self.count_txt).zfill(30),
                'date_time': str(formatted_date_time).split('.')[0].replace('-', '').replace(' ', '').replace(':', ''),
            }

        if self.journal_temporal_code == '09':
            report_txt = ReportInvBalTxt(False, False, line_data_scot, False, '09_txt')
            values_content = report_txt.get_content()

            report_zip = ReportInvBalTxt(False, False, line_data_scot, False, '09_zip')
            txt_2 = report_zip.get_content()

            data = {
                'txt_binary_scotia': base64.b64encode(values_content.encode() or '\n'.encode()),
                'txt_filename_scotia': 'Pago.txt',
                'txt_binary_scotia_zip': txt_2 or base64.b64encode(b'\n'),
                'txt_filename_scotia_zip': 'Pago.zip',
            }
            self.write(data)

        report_txt = ReportInvBalTxt(data_name, list_data, line_data, line_data_2, type_bank)

        values_content = report_txt.get_content()

        data = {
            'txt_binary_bank': base64.b64encode(values_content.encode() or '\n'.encode()),
            'txt_filename_bank': report_txt.get_filename(),
        }
        self.write(data)
        return
