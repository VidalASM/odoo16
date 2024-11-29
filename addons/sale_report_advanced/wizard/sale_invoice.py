# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import json
import io
from xlsxwriter import workbook
import pytz
from datetime import datetime, timedelta

from odoo.tools import date_utils
from odoo import fields, models

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class SaleReportAdvance(models.TransientModel):
    _name = "sale.report.invoice"

    customer_ids = fields.Many2many('res.partner', string="Clientes", required=True)
    from_date = fields.Date(string="Fecha Inicial")
    to_date = fields.Date(string="Fecha Final")
    status = fields.Selection([('open', 'Electrónico'), ('paid', 'Pagados'), ('both', 'Todo')],
                              string='Tipo', default='open', required=True)
    company_ids = fields.Many2many('res.company', string='Companies')
    today_date = fields.Date(default=fields.Date.today())

    def get_invoice_report(self):
        datas = self._get_data()
        return self.env.ref('sale_report_advanced.action_invoice_analysis').report_action([], data=datas)

    def _get_data(self):

        customers = []
        # sale = self.env['sale.order'].search([('state','!=','cancel')])

        # if self.from_date and self.to_date and self.company_ids:
        #     sales_order = list(filter(lambda
        #                                   x: x.date_order.date() >= self.from_date and x.date_order.date() <= self.to_date and x.company_id in self.company_ids,
        #                               sale))
        # elif not self.from_date and self.to_date and self.company_ids:
        #     sales_order = list(filter(lambda
        #                                   x: x.date_order.date() <= self.to_date and x.company_id in self.company_ids,
        #                               sale))
        # elif self.from_date and not self.to_date and self.company_ids:
        #     sales_order = list(filter(lambda
        #                                   x: x.date_order.date() >= self.from_date and x.company_id in self.company_ids,
        #                               sale))
        # elif self.from_date and self.to_date and not self.company_ids:
        #     sales_order = list(filter(lambda
        #                                   x: x.date_order.date() >= self.from_date and x.date_order.date() <= self.to_date,
        #                               sale))
        # elif not self.from_date and not self.to_date and self.company_ids:
        #     sales_order = list(filter(lambda
        #                                   x: x.company_id in self.company_ids,
        #                               sale))
        # elif not self.from_date and self.to_date and not self.company_ids:
        #     sales_order = list(filter(lambda
        #                                   x: x.date_order.date() <= self.to_date,
        #                               sale))
        # elif self.from_date and not self.to_date and not self.company_ids:
        #     sales_order = list(filter(lambda
        #                                   x: x.date_order.date() >= self.from_date,
        #                               sale))
        # else:
        #     sales_order = sale

        # result = []
        # customers = []
        # for rec in self.customer_ids:
        #     a = {
        #         'id': rec,
        #         'name': rec.name
        #     }
        #     customers.append(a)
        # for so in sales_order:
        #     for cust in customers:
        #         if cust['id'] == so['partner_id']:
        #             if so.invoice_ids:
        #                 if self.status == 'open':
        #                     for inv in so.invoice_ids:
        #                         if inv.payment_state != 'paid':
        #                             res = {
        #                                         'so': so.name,
        #                                         'partner_id': so.partner_id,
        #                                         'order_date': so.date_order,
        #                                         'invoice': inv.name,
        #                                         'date': inv.invoice_date,
        #                                         'invoiced': inv.amount_total,
        #                                         'paid': inv.amount_total-inv.amount_residual,
        #                                         'due': inv.amount_residual,
        #                                     }
        #                             result.append(res)
        #                 elif self.status == 'paid':
        #                     for inv in so.invoice_ids:
        #                         if inv.payment_state == 'paid':
        #                             res = {
        #                                         'so': so.name,
        #                                         'partner_id': so.partner_id,
        #                                         'order_date': so.date_order,
        #                                         'invoice': inv.name,
        #                                         'date': inv.invoice_date,
        #                                         'invoiced': inv.amount_total,
        #                                         'paid': inv.amount_total-inv.amount_residual,
        #                                         'due': inv.amount_residual,
        #                                     }
        #                             result.append(res)
        #                 else:
        #                     for inv in so.invoice_ids:
        #                         res = {
        #                                     'so': so.name,
        #                                     'partner_id': so.partner_id,
        #                                     'order_date': so.date_order,
        #                                     'invoice': inv.name,
        #                                     'date': inv.invoice_date,
        #                                     'invoiced': inv.amount_total,
        #                                     'paid': inv.amount_total-inv.amount_residual,
        #                                     'due': inv.amount_residual,
        #                                 }
        #                         result.append(res)

        lines = []
        searchv = [('company_id','=',self.env.user.company_id.id), ('move_type', 'in', ['out_invoice','out_refund']), ('invoice_date','>=',self.from_date), ('invoice_date','<=',self.to_date)]
        if self.status == 'paid':
            searchv.append(('payment_state','in',['in_payment','paid']))
        if self.status == 'open':
            searchv.append(('state','!=','draft'))
            searchv.append(('journal_id.l10n_pe_edi_is_einvoice','=',True))
        else:
            searchv.append(('state','!=','draft'))
        # print(searchv, self.env.user.company_id.name)
        invoices = self.env['account.move'].search(searchv, order='invoice_date asc')
        for invoice in invoices:
            payment_journals = ''
            references = ''
            reconciled_moves = []
            content = invoice.invoice_payments_widget['content'] if invoice.invoice_payments_widget else []
            for c in content:
                reconciled_moves.append(c['move_id'])
            payments = self.env['account.move'].browse(reconciled_moves).mapped('payment_id')
            payment_journals = ', '.join(str(x) for x in [payment.journal_id.name for payment in payments])
            references = ', '.join(str(x) for x in [payment.ref for payment in payments])

            status = ''
            if invoice.l10n_pe_edi_sunat_accepted:
                if invoice.l10n_pe_edi_sunat_accepted == True:
                    status = 'Aceptada'

            res = {
                'date': invoice.date,
                'l10n_pe_vat_code': invoice.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
                'vat': invoice.partner_id.vat,
                'partner_name': invoice.partner_id.name,
                'user_name': invoice.user_id.name,
                'invoice_date': invoice.invoice_date,
                'invoice_date_due': invoice.invoice_date_due,
                'document_type_code': invoice.l10n_latam_document_type_id.code,
                'document_type_name': invoice.l10n_latam_document_type_id.name,
                'sequence_prefix': invoice.sequence_prefix[0:4] if invoice.sequence_prefix else '',
                'sequence_number': invoice.sequence_number,
                'invoice_origin': invoice.invoice_origin,
                'payment_journals': payment_journals,
                'references': references,
                'amount_untaxed_signed': invoice.amount_untaxed_signed if invoice.state != 'cancel' else 0.0,
                'amount_tax_signed': invoice.amount_tax_signed if invoice.state != 'cancel' else 0.0,
                'amount_total_signed': invoice.amount_total_signed if invoice.state != 'cancel' else 0.0,
                'amount_residual_signed': invoice.amount_residual_signed if invoice.state != 'cancel' else 0.0,
                'status': status,
            }
            lines.append(res)
        #if pay_only:
            #invoices = invoices.search([('state','!=','draft')])
        # for invoice in invoices:
        #     add = False
        #     for payment in invoice.payment_ids:
        #         if payment.payment_date >= start_d and payment.payment_date <= end_d:
        #             add = True
        #     if pay_only and sfs_v:
        #         if invoice.elec_serie_id.is_factelec and add:
        #             lines.append(invoice)
        #     elif pay_only:
        #         if add:
        #             lines.append(invoice)
        #     elif sfs_v:
        #         if (str(invoice.date_invoice) >= start_d and str(invoice.date_invoice) <= end_d) and \
        #             invoice.elec_serie_id.is_factelec and invoice.state in ['open','paid','cancel']:
        #             lines.append(invoice)
        #     else:
        #         if (str(invoice.date_invoice) >= start_d and str(invoice.date_invoice) <= end_d) or add:
        #             lines.append(invoice)                
        # lines = sorted(lines, key=lambda x: str(x['number']))
        # return lines

        datas = {
            'ids': self,
            'model': 'sale.report.invoice',
            'form': lines,
            'partner_id': customers,
            'start_date': self.from_date,
            'end_date': self.to_date,
            'status': self.status,
        }

        return datas

    def get_excel_invoice_report(self):
        datas = self._get_data()
        return {
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'data': {'model': 'sale.report.invoice',
                     'output_format': 'xlsx',
                     'options': json.dumps(datas, default=date_utils.json_default),
                     'report_name': 'Excel Report Name',
                     },
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('REPORTE VENTAS')
        record =[]
        comp = self.env.user.company_id.name
        # cell_format = workbook.add_format({'font_size': '12px',})
        # head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '20px'})
        # txt = workbook.add_format({'font_size': '10px','align': 'center'})
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True, 'border': True, 'valign': 'vcenter', 'text_wrap': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'left', 'border': True})
        font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left', 'border': True})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right', 'border': True})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        green_mark = workbook.add_format({'font_size': 8, 'bg_color': 'green'})
        justify = workbook.add_format({'font_size': 12})
        format3.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')
        green_mark.set_align('center')

        sheet.set_row(10, 30)
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 11)
        sheet.set_column('C:C', 12)
        sheet.set_column('D:D', 35)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 10)
        sheet.set_column('G:G', 12)
        sheet.set_column('H:H', 13)
        sheet.set_column('I:I', 13)
        sheet.set_column('J:J', 8)
        sheet.set_column('K:L', 9)
        sheet.set_column('L:L', 10)
        sheet.set_column('M:M', 14)
        sheet.set_column('N:N', 14)
        sheet.set_column('O:R', 10)
        sheet.set_column('Q:Q', 10)

        # sheet.merge_range('G2:M3', 'Invoice Analysis Report', head)
        # if data['start_date'] and data['end_date']:
        #     sheet.write('G6', 'From:', cell_format)
        #     sheet.merge_range('H6:I6', data['start_date'], txt)
        #     sheet.write('K6', 'To:', cell_format)
        #     sheet.merge_range('L6:M6', data['end_date'], txt)

        sheet.merge_range(1, 4, 2, 10, 'REPORTE DE VENTAS', format0)
        sheet.merge_range(3, 4, 3, 10, comp, format11)
        sheet.merge_range(4, 0, 4, 1, 'Rango de Fechas : ', format4)
        sheet.merge_range(4, 2, 4, 4, str(data['start_date']) +
                          " - " + str(data['end_date']), format21)
        
        user = self.env['res.users'].browse(self.env.uid)
        tz = pytz.timezone(user.tz)
        time = pytz.utc.localize(datetime.now()).astimezone(tz)
        sheet.merge_range('A8:H8', 'Fecha de Reporte: ' + str(time.strftime("%Y-%m-%d %H:%M %p")), format1)

        sheet.merge_range(9, 0, 10, 0, 'FECHA', format21)
        sheet.merge_range(9, 1, 9, 3, 'DATOS DEL CLIENTE', format21)
        sheet.write(10, 1, 'TIPO DE DOCUMENTO', format21)
        sheet.write(10, 2, 'RUC/DNI', format21)
        sheet.write(10, 3, 'APELLIDOS Y NOMBRES O RAZÓN SOCIAL', format21)
        sheet.merge_range(9, 4, 10, 4, 'VENDEDOR', format21)
        sheet.merge_range(9, 5, 10, 5, 'FECHA DE EMISIÓN', format21)
        sheet.merge_range(9, 6, 10, 6, 'FECHA DE VENCIMIENTO', format21)
        sheet.merge_range(9, 7, 9, 10, 'DATOS DEL COMPROBANTE', format21)
        sheet.write(10, 7, 'CÓDIGO DE COMPROBANTE', format21)
        sheet.write(10, 8, 'COMPROBANTE', format21)
        sheet.write(10, 9, 'SERIE', format21)
        sheet.write(10, 10, 'NÚMERO', format21)
        sheet.merge_range(9, 11, 10, 11, 'DOC. ORIGEN', format21)
        sheet.merge_range(9, 12, 10, 12, 'TIPO DE PAGO', format21)
        sheet.merge_range(9, 13, 10, 13, 'REFERENCIA', format21)
        sheet.merge_range(9, 14, 10, 14, 'IMPORTE', format21)
        sheet.merge_range(9, 15, 10, 15, 'IGV', format21)
        sheet.merge_range(9, 16, 10, 16, 'TOTAL', format21)
        sheet.merge_range(9, 17, 10, 17, 'SALDO', format21)
        sheet.merge_range(9, 18, 10, 18, 'ESTADO', format21)

        prod_row = 11
        prod_col = 0

        sum_importe = 0
        sum_tax = 0
        sum_importe_total = 0
        sum_residual = 0

        for each in data['form']:
            sheet.write(prod_row, prod_col, each['date'], font_size_8)
            sheet.write(prod_row, prod_col + 1, each['l10n_pe_vat_code'], font_size_8_l)
            sheet.write(prod_row, prod_col + 2, each['vat'], font_size_8_r)
            sheet.write(prod_row, prod_col + 3, each['partner_name'], font_size_8_l)
            sheet.write(prod_row, prod_col + 4, each['user_name'], font_size_8_l)
            sheet.write(prod_row, prod_col + 5, each['invoice_date'], font_size_8_l)
            sheet.write(prod_row, prod_col + 6, each['invoice_date_due'], font_size_8_l)
            sheet.write(prod_row, prod_col + 7, each['document_type_code'], font_size_8_l)
            sheet.write(prod_row, prod_col + 8, each['document_type_name'], font_size_8_r)
            sheet.write(prod_row, prod_col + 9, each['sequence_prefix'], font_size_8_r)
            sheet.write(prod_row, prod_col + 10, each['sequence_number'], font_size_8_r)
            sheet.write(prod_row, prod_col + 11, each['invoice_origin'], font_size_8_r)
            sheet.write(prod_row, prod_col + 12, each['payment_journals'], font_size_8_l)
            sheet.write(prod_row, prod_col + 13, each['references'], font_size_8_l)
            sheet.write(prod_row, prod_col + 14, each['amount_untaxed_signed'], font_size_8_r)
            sheet.write(prod_row, prod_col + 15, each['amount_tax_signed'], font_size_8_r)
            sheet.write(prod_row, prod_col + 16, each['amount_total_signed'], font_size_8_r)
            sheet.write(prod_row, prod_col + 17, each['amount_residual_signed'], font_size_8_r)
            sheet.write(prod_row, prod_col + 18, each['status'], font_size_8_r)

            sum_importe = sum_importe + each['amount_untaxed_signed']
            sum_tax = sum_tax + each['amount_tax_signed']
            sum_importe_total = sum_importe_total + each['amount_total_signed']
            sum_residual = sum_residual + each['amount_residual_signed']

            prod_row = prod_row + 1
    
        sheet.merge_range(prod_row, 0, prod_row, prod_col + 12, "")
        sheet.write(prod_row, 13, 'TOTAL', format21)
        sheet.write(prod_row, 14, sum_importe, font_size_8_r)
        sheet.write(prod_row, 15, sum_tax, font_size_8_r)
        sheet.write(prod_row, 16, sum_importe_total, font_size_8_r)
        sheet.write(prod_row, 17, sum_residual, font_size_8_r)

        # format1 = workbook.add_format(
        #     {'font_size': 10, 'align': 'left','bg_color':'#bbd5fc','border': 1})
        # format4 = workbook.add_format(
        #     {'font_size': 10, 'align': 'center', 'bg_color': '#bbd5fc', 'border': 1})
        # format2 = workbook.add_format(
        #     {'font_size': 10, 'align': 'center', 'bold': True,
        #      'bg_color': '#6BA6FE', 'border': 1})
        # format3 = workbook.add_format(
        #     {'font_size': 10, 'align': 'center', 'bold': True})
        # record = data['partner_id']
        # h_row = 7
        # h_col = 9
        # count = 0
        # row = 5
        # col = 6
        # row_number = 6
        # t_row = 6
        # if data['partner_id']:
        #     for rec in record:
        #         sheet.merge_range(h_row, h_col-3,h_row,h_col+3, rec['name'], format4)
        #         row= row + count + 3
        #         sheet.write(row, col, 'Order Number', format2)
        #         sheet.set_column('G:G', 12)
        #         col += 1
        #         sheet.write(row, col, 'Order Date', format2)
        #         sheet.set_column('H:H', 15)
        #         col += 1
        #         sheet.write(row, col, 'Invoice Number', format2)
        #         sheet.set_column('I:I', 13)
        #         col += 1
        #         sheet.write(row, col, 'Invoice Date', format2)
        #         sheet.set_column('J:J', 15)
        #         col += 1
        #         sheet.write(row, col, 'Amount Invoiced', format2)
        #         sheet.set_column('K:K', 11)
        #         col += 1
        #         sheet.write(row, col, 'Amount Paid', format2)
        #         sheet.set_column('L:L', 11)
        #         col += 1
        #         sheet.write(row, col, 'Amount Due', format2)
        #         sheet.set_column('M:M', 11)
        #         col += 1
        #         col =6
        #         count=0
        #         t_invoiced = 0
        #         t_paid = 0
        #         t_due = 0
        #         row_number=row_number + count + 3
        #         t_col = 9
        #         for val in data['form']:
        #             if val['partner_id'] == rec['id']:
        #                 count +=1
        #                 column_number = 6
        #                 sheet.write(row_number, column_number, val['so'],format1)
        #                 sheet.set_column('G:G', 12)
        #                 column_number += 1
        #                 sheet.write(row_number, column_number, val['order_date'], format1)
        #                 sheet.set_column('H:H', 15)
        #                 column_number += 1
        #                 sheet.write(row_number, column_number, val['invoice'], format1)
        #                 sheet.set_column('I:I', 13)
        #                 column_number += 1
        #                 sheet.write(row_number, column_number, val['date'], format1)
        #                 sheet.set_column('J:J', 15)
        #                 column_number += 1
        #                 sheet.write(row_number, column_number, val['invoiced'], format1)
        #                 sheet.set_column('K:K', 14)
        #                 t_invoiced += val['invoiced']
        #                 column_number += 1
        #                 sheet.write(row_number, column_number, val['paid'], format1)
        #                 sheet.set_column('L:L', 11)
        #                 t_paid += val['paid']
        #                 column_number += 1
        #                 sheet.write(row_number, column_number, val['due'], format1)
        #                 sheet.set_column('M:M', 11)
        #                 t_due += val['due']
        #                 row_number += 1
        #         t_row = t_row + count + 3
        #         sheet.write(t_row, t_col, 'Total', format3)
        #         sheet.set_column('J:J', 15)
        #         t_col += 1
        #         sheet.write(t_row, t_col, t_invoiced, format3)
        #         sheet.set_column('K:K', 14)
        #         t_col += 1
        #         sheet.write(t_row, t_col, t_paid, format3)
        #         sheet.set_column('L:L', 11)
        #         t_col += 1
        #         sheet.write(t_row, t_col, t_due, format3)
        #         sheet.set_column('M:M', 11)
        #         h_row = h_row + count + 3
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
