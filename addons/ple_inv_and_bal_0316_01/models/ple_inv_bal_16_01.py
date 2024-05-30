from odoo import fields, models, api
from datetime import date
from ..reports.report_inv_bal_16_01 import ReportInvBalSixteenExcel, ReportInvBalSixteenTxt
import base64


class PleInvBal106(models.Model):
    _name = 'ple.report.inv.bal.16.1'
    _description = 'Cuentas por Cobrar Diversas de Terceros y Relacionadas'
    _inherit = 'ple.report.base'

    line_ids_316_01 = fields.One2many(
        comodel_name='ple.report.inv.bal.line.16.1',
        inverse_name='report_id',
    )

    financial_statements_catalog = fields.Selection(
        selection=[
            ('01', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR DIVERSAS - INDIVIDUAL'),
            ('02', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR SEGUROS - INDIVIDUAL'),
            ('03', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR BANCOS Y FINANCIERAS - INDIVIDUAL'),
            ('04', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - ADMINISTRADORAS DE FONDOS DE PENSIONES (AFP)'),
            ('05', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - AGENTES DE INTERMEDIACIÓN'),
            ('06', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - FONDOS DE INVERSIÓN'),
            ('07', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - PATRIMONIO EN FIDEICOMISOS'),
            ('08', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - ICLV'),
            ('09', 'OTROS NO CONSIDERADOS EN LOS ANTERIORES')
        ],
        string='Catálogo estados financieros',
        default='09',
        required=True
    )
    eeff_presentation_opportunity = fields.Selection(
        selection=[
            ('01', 'Al 31 de diciembre'),
            ('02', 'Al 31 de enero, por modificación del porcentaje'),
            ('03', 'Al 30 de junio, por modificación del coeficiente o porcentaje'),
            ('04',
             'Al último día del mes que sustentará la suspensión o modificación del coeficiente (distinto al 31 de enero o 30 de junio)'),
            ('05',
             'Al día anterior a la entrada en vigencia de la fusión, escisión y demás formas de reorganización de sociedades o emperesas o extinción '
             'de la persona jurídica'),
            ('06', 'A la fecha del balance de liquidación, cierre o cese definitivo del deudor tributario'),
            ('07', 'A la fecha de presentación para libre propósito')
        ],
        string='Oportunidad de presentación de EEFF',
        required=True
    )

    txt_filename = fields.Char(string='Filename .txt')
    txt_binary = fields.Binary(string='Reporte .TXT 3.16.1')

    pdf_filename = fields.Char(string='Filename .txt')
    pdf_binary = fields.Binary(string='Reporte .TXT 3.16.1')

    def _set_values(self, obj_move_line):
        partner = obj_move_line.partner_id or self.env.company.partner_id
        values = {
            'partner': partner.name,
            'move': obj_move_line.move_id.name or '',
            'name': obj_move_line.name or '',
            'ref': obj_move_line.ref or '',
            'name_currency': obj_move_line.currency_id.name or '',
            'account_currency': obj_move_line.account_id.currency_id.name or '',
            'date_maturity': obj_move_line.date_maturity or '',
            'vat': partner.vat or '0',
            'ple_correlative': obj_move_line.ple_correlative or '',
            'l10n_latam_identification_type_id': partner.l10n_latam_identification_type_id.l10n_pe_vat_code or '',
        }
        return values

    def generate_data(self):
        account_ids = self.env['account.account'].search([('group_id.code_prefix_start', '=', '50')])
        data_account = {}
        for obj_account in account_ids:
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
                        'account': obj_account.code,
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
                            'account': obj_account.code,
                            'amount_currency': 0.00,
                            'date_maturity': obj_ml.date_maturity or '',
                            'date_reconcile': date.strftime(reconcile_date, '%d/%m/%Y'),
                            'reconcile': obj_ml.full_reconcile_id.name,
                        }
                        values.update(self._set_values(obj_ml))
                        dict_group.setdefault(obj_ml.full_reconcile_id.id, values)
                        dict_group[obj_ml.full_reconcile_id.id]['balance'] += obj_ml.balance
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
                            'date': date.strftime(list_ml[0].date, '%d/%m/%Y'),
                            'balance': 0.00,
                            'amount_currency': 0.00,
                            'move_line_id': list_ml[0].id,
                            'account': obj_account.code
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
                        'account': obj_account.code,
                    }
                    values.update(self._set_values(obj_ml_zero))
                    data_account[name_account].append(values)
        return data_account

    def action_generate_excel(self):
        self.ensure_one()
        data = self.generate_data()

        report_xls = ReportInvBalSixteenExcel(self, data)
        values_content_xls = report_xls.get_content()
        self.xls_binary = base64.b64encode(values_content_xls)
        self.xls_filename = report_xls.get_filename()

        report_txt = ReportInvBalSixteenTxt(self, data)
        values_content_txt = report_txt.get_content()
        self.txt_binary = base64.b64encode(values_content_txt.encode() or '\n'.encode())
        self.txt_filename = report_txt.get_filename()

        report_name = "ple_inv_and_bal_0316_01.action_print_status_finance"
        pdf = self.env.ref(report_name)._render_qweb_pdf('ple_inv_and_bal_0316_01.print_status_finance', self.id)[0]
        self.pdf_binary = base64.encodebytes(pdf)
        self.pdf_filename = f"Libro_Capital_{self.date_end.strftime('%Y%m')}.pdf"

        self.line_ids_316_01.unlink()

    def action_close(self):
        self.write({'state': 'closed'})

    def action_rollback(self):
        self.write({'state': 'draft'})
        self.write({
            'txt_binary': False,
            'txt_filename': False,
            'xls_binary': False,
            'xls_filename': False,
            'pdf_binary': False,
            'pdf_filename': False,
            'line_final_ids': False,
            'line_ids': False,
        })


class PleInvBalLines(models.Model):
    _name = 'ple.report.inv.bal.line.16.1'
    _description = 'Cuentas por cobrar - Líneas'
    balance = fields.Integer(string='Código de catálogo')
    report_id = fields.Many2one('ple.report.inv.bal.16.1')
