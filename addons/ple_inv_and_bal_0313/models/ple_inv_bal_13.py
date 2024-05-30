from odoo import fields, models, api
from odoo.exceptions import ValidationError
import base64
from datetime import date, datetime
from ..reports.report_inv_bal_13 import ReportInvBal13Excel, ReportInvBal13Txt
import re


class PleInvBal13(models.Model):
    _inherit = 'ple.report.inv.bal.one'

    xls_filename_313 = fields.Char(string='Filaname_13 Excel')
    xls_binary_313 = fields.Binary(string='Reporte Excel')
    txt_filename_313 = fields.Char(string='Filaname_13 .txt')
    txt_binary_313 = fields.Binary(string='Reporte .TXT 3.13')
    pdf_filename_313 = fields.Char(string='Filaname_13 .pdf')
    pdf_binary_313 = fields.Binary(string='Reporte .PDF 3.13')

    line_ids_313 = fields.One2many(
        comodel_name='ple.report.inv.bal.line.13', inverse_name='ple_report_inv_val_13_id')

    def action_generate_excel(self):
        super().action_generate_excel()
        data = self.generate_data_report_313()

        report_xls = ReportInvBal13Excel(self, data)
        values_content_xls = report_xls.get_content()
        self.xls_binary_313 = base64.b64encode(values_content_xls)
        self.xls_filename_313 = report_xls.get_filename()

        report_txt = ReportInvBal13Txt(self, data)
        values_content_txt = report_txt.get_content()
        self.txt_binary_313 = base64.b64encode(
            values_content_txt.encode() or '\n'.encode())
        self.txt_filename_313 = report_txt.get_filename()

        report_name = "ple_inv_and_bal_0313.action_print_status_finance"
        pdf = self.env.ref(report_name)._render_qweb_pdf(
            'ple_inv_and_bal_0313.print_status_finance', self.id)[0]
        self.pdf_binary_313 = base64.encodebytes(pdf)
        self.pdf_filename_313 = f"Libro_Cuentas_por_pagar_diversas_{self.date_end.strftime('%Y%m')}.pdf"

        self.line_ids_313.unlink()

    def _set_values(self, obj_move_line):
        partner = obj_move_line.partner_id or self.env.company.partner_id
        values = {
            'partner': partner.name,
            'move': re.sub("\-|\ |\/", "", obj_move_line.name) or '',
            'vat': partner.vat or '0',
            'ple_correlative': obj_move_line.ple_correlative or '',
            'code': obj_move_line.account_id.code or '',
            'l10n_latam_identification_type_id': partner.l10n_latam_identification_type_id.l10n_pe_vat_code or '',
        }
        return values

    def generate_data_report_313(self):

        data_account = {}
        objs = self.env['account.account'].search(
            [('group_id.code_prefix_start', 'in', ('46', '47'))])
        for obj_account in objs:

            name_account = '{} {}'.format(
                obj_account.code,
                obj_account.name
            )
            data_account.setdefault(name_account, [])

            if not obj_account.reconcile:
                if obj_account.user_type_id.include_initial_balance:

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
                    sum_currency = sum(
                        map(lambda x: x.amount_currency, list_move_line))
                    name_etiqueta = map(lambda x: x.name, list_move_line)
                    values = {
                        'date': date.strftime(self.date_end, '%d/%m/%Y'),
                        'balance': sum_balance,
                        'amount_currency': sum_currency,
                        'name': name_etiqueta
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

                list_ml_reconcile = list_move_line.filtered(
                    lambda x: x.full_reconcile_id in list_full_reconcile)
                list_ml_zero = list_move_line.filtered(
                    lambda x: not x.full_reconcile_id and not x.matched_debit_ids and not x.matched_credit_ids)

                list_ml_unreconcile = list_move_line.filtered(
                    lambda x: not x.full_reconcile_id)
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
                            'name': list_move_line.name

                        }
                        values.update(self._set_values(obj_ml))
                        dict_group.setdefault(
                            obj_ml.full_reconcile_id.id, values)
                        dict_group[obj_ml.full_reconcile_id.id]['balance'] += obj_ml.balance
                        dict_group[obj_ml.full_reconcile_id.id]['amount_currency'] += obj_ml.amount_currency
                    data_account[name_account].extend(
                        map(lambda x: dict_group[x], dict_group.keys()))
                if list_ml_unreconcile_filter:
                    list_unreconcile_ml = []
                    dict_temporal = {}

                    list_obj_partial_reconcile = self.env['account.partial.reconcile'].search(
                        [], order='max_date')
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
                                    list_unreconcile_ml[i].extend(
                                        list(list_item))
                                    dict_temporal[i].extend(list(list_item))
                                    e = i
                                else:
                                    if e:
                                        dict_temporal[e].extend(
                                            list_unreconcile_ml[i])
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
                                dict_temporal.update(
                                    {len(list_unreconcile_ml) - 1: list_value})

                    list_unreconcile_set = [
                        list(set(dict_temporal[key])) for key in dict_temporal]
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
                        'name': obj_ml_zero.name
                    }
                    values.update(self._set_values(obj_ml_zero))
                    data_account[name_account].append(values)

        values_ple_report_inv_bal_line_13 = []
        for value in data_account.keys():
            if data_account[value]:
                for datos in data_account[value]:
                    values_ple_report_inv_bal_line_13.append({
                        'document_name': datos['name'] if datos and 'name' in datos.keys() and datos['name'] else '',
                        'date_issue': datetime.strptime(datos['date'], '%d/%m/%Y').date() if datos['date'] else '',
                        'code': datos['code'],
                        'correlative': datos['ple_correlative'],
                        'type_document_third': datos['l10n_latam_identification_type_id'],
                        'tax_identification_number': datos['vat'],
                        'business_name': datos['partner'],
                        'provision_amount': datos['balance'],
                        'name': date.strftime(self.date_end, '%Y%m%d')
                    })
        self.env['ple.report.inv.bal.line.13'].create(
            values_ple_report_inv_bal_line_13).ids
        return values_ple_report_inv_bal_line_13


class PleInvBalLines(models.Model):
    _name = 'ple.report.inv.bal.line.13'
    _description = 'Reporte 3.13 - Líneas'

    catalog_code = fields.Char(string='Código de catálogo')
    document_name = fields.Char(string='Nombre de la Factura')
    name = fields.Char(string="Periodo")
    accounting_seat = fields.Char(string="CUO")
    correlative = fields.Char(string="Correlativo")
    type_document_third = fields.Integer(string="Tipo de Documento Tercero")
    tax_identification_number = fields.Char(
        string="Numero de Documento Tercero")
    date_issue = fields.Date(string='Fecha de Emisión del Comprobante de Pago')
    code = fields.Char(string='Código de la Cuenta Contable')
    business_name = fields.Char(string="Apellidos y Nombres de Terceros")
    provision_amount = fields.Float(
        string="Monto Pendiente de Pago al Tercero")
    account_status = fields.Integer(string="Estado de la operación")
    free_field = fields.Char(string="Campo libre")
    ple_report_inv_val_13_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.one')
