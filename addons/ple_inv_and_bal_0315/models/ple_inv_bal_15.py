from odoo import fields, models, api
from odoo.exceptions import ValidationError
import base64
from datetime import date, datetime
from ..reports.report_inv_bal_15 import ReportInvBal15Excel, ReportInvBal15Txt
import re


class PleInvBal15(models.Model):
    _inherit = 'ple.report.inv.bal.one'

    xls_filename_315 = fields.Char(string='Filaname_15 Excel')
    xls_binary_315 = fields.Binary(string='Reporte Excel')
    txt_filename_315 = fields.Char(string='Filaname_15 .txt')
    txt_binary_315 = fields.Binary(string='Reporte .TXT 3.15')
    pdf_filename_315 = fields.Char(string='Filaname_15 .pdf')
    pdf_binary_315 = fields.Binary(string='Reporte .PDF 3.15')

    line_ids_315 = fields.One2many(comodel_name='ple.report.inv.bal.line.15', inverse_name='ple_report_inv_val_15_id')

    def action_generate_excel(self):
        super().action_generate_excel()
        data = self.generate_data_report_315()

        report_xls = ReportInvBal15Excel(self, data)
        values_content_xls = report_xls.get_content()
        self.xls_binary_315 = base64.b64encode(values_content_xls)
        self.xls_filename_315 = report_xls.get_filename()

        report_txt = ReportInvBal15Txt(self, data)
        values_content_txt = report_txt.get_content()
        self.txt_binary_315 = base64.b64encode(values_content_txt.encode() or '\n'.encode())
        self.txt_filename_315 = report_txt.get_filename()

        report_name = "ple_inv_and_bal_0315.action_print_status_finance"
        pdf = self.env.ref(report_name)._render_qweb_pdf('ple_inv_and_bal_0315.print_status_finance', self.id)[0]
        self.pdf_binary_315 = base64.encodebytes(pdf)
        self.pdf_filename_315 = f"Libro_Activos_Pasivos_Diferidos_{self.date_end.strftime('%Y%m')}.pdf"

        self.line_ids_315.unlink()

    def _set_values(self, obj_move_line):
        partner = obj_move_line.partner_id or self.env.company.partner_id
        related_payment_voucher = ''
        serial_number_payment = ''
        if obj_move_line.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
            related_payment_voucher = obj_move_line.name.replace(' ', '')[6:9]
            serial_number_payment = obj_move_line.name.replace(' ', '')[1:5]
        elif obj_move_line.move_type in ['in_invoice', 'in_refund', 'in_receipt'] and obj_move_line.ref:
            related_payment_voucher = obj_move_line.ref.replace(' ', '')[6:9]
            serial_number_payment = obj_move_line.ref.replace(' ', '')[1:5]
        elif obj_move_line.move_type == 'entry':
            related_payment_voucher = '00000000'
            serial_number_payment = '0000'

        values = {
            'ref':  obj_move_line.ref or '',
            'partner': partner.name,
            'move': re.sub("\-|\ |\/", "", obj_move_line.move_id.name) or '',
            'vat': partner.vat or '0',
            'ple_correlative': obj_move_line.ple_correlative or '',
            'code': obj_move_line.account_id.code or '',
            'l10n_latam_identification_type_id': partner.l10n_latam_identification_type_id.l10n_pe_vat_code or '',
            'related_payment_voucher': related_payment_voucher,
            'serial_number_payment': serial_number_payment,
            'type_l10n_latam_identification': obj_move_line.l10n_latam_document_type_id.code or '00'
        }
        return values
    def generate_data_report_315(self):
        data_account = {}
        objs = self.env['account.account'].search([('group_id.code_prefix_start', 'in', ('37', '49'))])
        for obj_account in objs:

            name_account = '{} {}'.format(
                obj_account.code,
                obj_account.name
            )
            data_account.setdefault(name_account, [])

            if not obj_account.reconcile:
                if obj_account.include_initial_balance:

                    list_move_line = self.env['account.move.line'].search([
                        ('account_id', '=', obj_account.id),
                        ('date', '<=', self.date_end),
                        ('parent_state', '=', 'posted')
                    ], order='id')
                else:
                    list_move_line = self.env['account.move.line'].search([
                        ('account_id', '=', obj_account.id),
                        ('date', '>=', self.date_start),
                        ('date', '<=', self.date_end),
                        ('parent_state', '=', 'posted')
                    ], order='id')

                if list_move_line:
                    sum_balance = sum(map(lambda x: x.balance, list_move_line))
                    sum_currency = sum(map(lambda x: x.amount_currency, list_move_line))
                    values = {
                        'date': date.strftime(self.date_end, '%d/%m/%Y'),
                        'balance': sum_balance,
                        'amount_currency': sum_currency
                    }
                    values.update(self._set_values(list_move_line[0]))
                    data_account[name_account].append(values)
            else:
                list_full_reconcile = self.env['account.full.reconcile'].search([
                    ('reconcile_date', '>', self.date_end)
                ])
                list_move_line = self.env['account.move.line'].search([
                    ('account_id', '=', obj_account.id),
                    ('date', '<=', self.date_end),
                    ('parent_state', '!=', 'cancel')
                ], order='id')

                list_ml_reconcile = list_move_line.filtered(lambda x: x.full_reconcile_id in list_full_reconcile)
                list_ml_zero = list_move_line.filtered(
                    lambda x: not x.full_reconcile_id and not x.matched_debit_ids and not x.matched_credit_ids)

                list_ml_unreconcile = list_move_line.filtered(lambda x: not x.full_reconcile_id)
                list_ml_unreconcile_filter = []
                for _item in list_ml_unreconcile:
                    if _item not in list_ml_zero:
                        list_ml_unreconcile_filter.append(_item)

                if list_ml_reconcile:
                    dict_group = {}
                    for obj_ml in list_ml_reconcile:
                        reconcile_date = obj_ml.full_reconcile_id.reconcile_date
                        values = {
                            'date': date.strftime(obj_ml.date, '%d/%m/%Y'),
                            'balance': 0.00,
                            'amount_currency': 0.00,

                        }
                        values.update(self._set_values(obj_ml))
                        dict_group.setdefault(obj_ml.full_reconcile_id.id, values)
                        dict_group[obj_ml.full_reconcile_id.id]['balance'] += obj_ml.balance
                        dict_group[obj_ml.full_reconcile_id.id]['amount_currency'] += obj_ml.amount_currency
                    data_account[name_account].extend(map(lambda x: dict_group[x], dict_group.keys()))
                if list_ml_unreconcile_filter:
                    list_unreconcile_ml = []
                    dict_temporal = {}

                    list_obj_partial_reconcile = self.env['account.partial.reconcile'].search([], order='max_date')
                    for obj_reconcile in list_obj_partial_reconcile:
                        obj_ml1 = False
                        obj_ml2 = False
                        bool_exist = False
                        if obj_reconcile.debit_move_id in list_ml_unreconcile_filter:
                            obj_ml1 = obj_reconcile.debit_move_id
                        if obj_reconcile.credit_move_id in list_ml_unreconcile_filter:
                            obj_ml2 = obj_reconcile.credit_move_id

                        list_item = (
                            obj_ml1,
                            obj_ml2) if obj_ml1 and obj_ml2 else obj_ml1 if obj_ml1 else obj_ml2 if obj_ml2 else ()
                        e = False
                        for i in range(len(list_unreconcile_ml)):
                            if obj_ml1 in list_unreconcile_ml[i] or obj_ml2 in list_unreconcile_ml[i]:
                                if not bool_exist:
                                    bool_exist = True
                                    dict_temporal.update({
                                        i: list_unreconcile_ml[i]
                                    })
                                    list_unreconcile_ml[i].extend(list(list_item))
                                    dict_temporal[i].extend(list(list_item))
                                    e = i
                                else:
                                    if e:
                                        dict_temporal[e].extend(list_unreconcile_ml[i])
                                        if dict_temporal.get(i):
                                            del dict_temporal[i]

                        if not bool_exist:
                            list_value = []
                            if obj_ml1:
                                list_value.append(obj_ml1)
                            if obj_ml2:
                                list_value.append(obj_ml2)
                            if list_value:
                                list_unreconcile_ml.append(list_value)
                                dict_temporal.update({len(list_unreconcile_ml) - 1: list_value})

                    list_unreconcile_set = [list(set(dict_temporal[key])) for key in dict_temporal]
                    for list_ml in list_unreconcile_set:
                        data_d = {
                            'date': date.strftime(list_ml[0].date, '%d/%m/%Y'),
                            'balance': 0.00,
                            'amount_currency': 0.00,
                            'move_line_id': list_ml[0].id,
                        }
                        data_d.update(self._set_values(list_ml[0]))
                        for i in range(len(list_ml)):
                            data_d['balance'] += list_ml[i].balance
                            data_d['amount_currency'] += list_ml[i].amount_currency
                            if data_d['move_line_id'] > list_ml[i].id:
                                data_d.update({
                                    'date': date.strftime(list_ml[i].date, '%d/%m/%Y'),
                                    'move_line_id': list_ml[i].id,
                                })
                                data_d.update(self._set_values(list_ml[i]))
                        data_account[name_account].append(data_d)
                for obj_ml_zero in list_ml_zero:
                    values = {
                        'date': date.strftime(obj_ml_zero.date, '%d/%m/%Y'),
                        'balance': obj_ml_zero.balance,
                        'amount_currency': obj_ml_zero.amount_currency,
                    }
                    values.update(self._set_values(obj_ml_zero))
                    data_account[name_account].append(values)

        values_ple_report_inv_bal_line_15 = []
        for value in data_account.keys():
            if data_account[value]:
                for datos in data_account[value]:
                    values_ple_report_inv_bal_line_15.append({
                        'document_name': datos['move'],
                        'ref': datos['ref'],
                        'code': datos['code'],
                        'correlative': datos['ple_correlative'],
                        'name': date.strftime(self.date_end, '%Y%m%d'),
                        'outstanding_balance': datos['balance'],
                        'related_payment_voucher': datos['related_payment_voucher'],
                        'serial_number_payment': datos['serial_number_payment'],
                        'type_l10n_latam_identification': datos['type_l10n_latam_identification']
                    })
        self.env['ple.report.inv.bal.line.15'].create(values_ple_report_inv_bal_line_15).ids
        return values_ple_report_inv_bal_line_15


class PleInvBalLines(models.Model):
    _name = 'ple.report.inv.bal.line.15'
    _description = 'Reporte 3.15 - Líneas'

    catalog_code = fields.Char(string='Código de catálogo')
    document_name = fields.Char(string='Nombre del documento')
    name = fields.Char(string='Periodo')
    accounting_seat = fields.Char(string='CUO')
    serial_number_payment = fields.Char(string='Número Serie del Comprobante de Pago')
    related_payment_voucher = fields.Char(string='Número del Comprobante de Pago Relacionado')
    correlative = fields.Char(string='Correlativo')
    ref = fields.Char(string='Referencia Factura')
    type_l10n_latam_identification = fields.Char(string='Tipo de Comprobante de Pago')
    code = fields.Char(string='Código de la Cuenta Contable')
    additions = fields.Float(string='Adiciones')
    deductions = fields.Float(string='Deducciones')
    outstanding_balance = fields.Float(string='Saldo Pendiente')
    free_field = fields.Char(string='Campo libre')
    ple_report_inv_val_15_id = fields.Many2one(comodel_name='ple.report.inv.bal.one')