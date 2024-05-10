from odoo import fields, models, api
from odoo.exceptions import ValidationError
import base64
from datetime import date
from ..reports.report_inv_bal_11 import ReportInvBal11Excel, ReportInvBal11Txt
import re


class PleInvBal11(models.Model):
    _inherit = 'ple.report.inv.bal.one'

    xls_filename_311 = fields.Char(string='Filaname_0311 Excel')
    xls_binary_311 = fields.Binary(string='Reporte Excel')
    txt_filename_311 = fields.Char(string='Filaname_0311 .txt')
    txt_binary_311 = fields.Binary(string='Reporte .TXT 3.11')
    pdf_filename_311 = fields.Char(string='Filaname_0311 .pdf')
    pdf_binary_311 = fields.Binary(string='Reporte .PDF 3.11')

    line_ids_311 = fields.One2many(comodel_name='ple.report.inv.bal.line.11', inverse_name='report_id')

    def action_generate_excel(self):
        super().action_generate_excel()
        data = self.generate_data_report_311()

        report_xls = ReportInvBal11Excel(self, data)
        values_content_xls = report_xls.get_content()
        self.xls_binary_311 = base64.b64encode(values_content_xls)
        self.xls_filename_311 = report_xls.get_filename()

        report_txt = ReportInvBal11Txt(self, data)
        values_content_txt = report_txt.get_content()
        self.txt_binary_311 = base64.b64encode(values_content_txt.encode() or '\n'.encode())
        self.txt_filename_311 = report_txt.get_filename()

        report_name = "ple_inv_and_bal_0311_0314.action_print_report_pdf_0311"
        pdf = self.env.ref(report_name)._render_qweb_pdf('ple_inv_and_bal_0311_0314.print_report_pdf_0311',self.id)[0]
        self.pdf_binary_311 = base64.encodebytes(pdf)
        self.pdf_filename_311 = f"Libro_Remuner_Particip_por_pagar_{self.date_end.strftime('%Y%m')}.pdf"

        self.line_ids_311.unlink()

    def _set_values_11(self, obj_move_line):
        partner = obj_move_line.partner_id or self.env.company.partner_id
        values = {
            'partner': partner.name,
            'move': re.sub("\-|\ |\/", "", obj_move_line.move_id.name) or '',
            'vat': partner.vat or '0',
            'ple_correlative': obj_move_line.ple_correlative or '',
            'l10n_latam_identification_type_id': partner.l10n_latam_identification_type_id.l10n_pe_vat_code or '',
        }
        return values

    def generate_data_report_311(self):
        data_account = {}
        objs = self.env['account.account'].search([
            ('group_id.code_prefix_start', '=', '41'),
            ('ple_selection', '=', 'assets_book_remuneration_contributions_payable')
        ])
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
                    sum_currency = sum(map(lambda x: x.amount_currency, list_move_line))
                    values = {
                        'balance': sum_balance,
                        'account': obj_account.code,
                        'name': obj_account.name,
                        'amount_currency': sum_currency,
                    }
                    values.update(self._set_values_11(list_move_line[0]))
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
                            'balance': 0.00,
                            'account': obj_account.code,
                            'amount_currency': 0.00,
                            'name': obj_account.name,

                        }
                        values.update(self._set_values_11(obj_ml))
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
                            obj_ml1, obj_ml2) if obj_ml1 and obj_ml2 else obj_ml1 if obj_ml1 else obj_ml2 if obj_ml2 else ()
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
                            'balance': 0.00,
                            'amount_currency': 0.00,
                            'move_line_id': list_ml[0].id,
                            'account': obj_account.code,
                            'name': obj_account.name,
                        }
                        data_d.update(self._set_values_11(list_ml[0]))
                        for i in range(len(list_ml)):
                            data_d['balance'] += list_ml[i].balance
                            data_d['amount_currency'] += list_ml[i].amount_currency
                            if data_d['move_line_id'] > list_ml[i].id:
                                data_d.update({
                                    'move_line_id': list_ml[i].id,
                                })
                                data_d.update(self._set_values_11(list_ml[i]))
                        data_account[name_account].append(data_d)
                for obj_ml_zero in list_ml_zero:
                    values = {
                        'balance': obj_ml_zero.balance,
                        'amount_currency': obj_ml_zero.amount_currency,
                        'account': obj_account.code,
                        'name': obj_account.name,
                    }
                    values.update(self._set_values_11(obj_ml_zero))
                    data_account[name_account].append(values)
        return data_account


class PleInvBalLines11(models.Model):
    _name = 'ple.report.inv.bal.line.11'
    _description = 'Reporte 3.11 - Líneas'

    report_id = fields.Many2one('ple.report.inv.bal.one')

    move = fields.Char()
    ple_correlative = fields.Char()
    account = fields.Char()
    l10n_latam_identification_type_id = fields.Char()
    vat = fields.Char()
    partner = fields.Char()
    balance = fields.Float()
    date = fields.Char()
    name = fields.Char()
