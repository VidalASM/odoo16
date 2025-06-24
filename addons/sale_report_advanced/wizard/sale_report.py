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
from datetime import datetime
from xlsxwriter import workbook

from odoo.tools import date_utils
from odoo import fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import pytz

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class SaleReportAdvance(models.TransientModel):
    _name = "sale.report.advance"

    def _default_first_day(self):
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        cmonth = datetime.now().month
        cyear = datetime.now().year
        return datetime.strptime('%s-%s-01' % (cyear,cmonth),'%Y-%m-%d')

    user_ids = fields.Many2many('res.users', string="Vendedores")
    customer_ids = fields.Many2many('res.partner', string="Clientes")
    product_ids = fields.Many2many('product.product', string='Productos')
    from_date = fields.Date(string="Fecha inicial", required=True, default=_default_first_day)
    to_date = fields.Date(string="Fecha Final", required=True, default=fields.Date.today())
    type = fields.Selection([('customer', 'Clientes'), ('product', 'Productos'), ('both', 'Ambos')], 
        string='Imprimir reporte por', default='customer', required=True)
    company_ids = fields.Many2many('res.company', string='Sedes')
    today_date = fields.Date(default=fields.Date.today())
    renovations = fields.Boolean(string='Renovaciones')
    complete = fields.Boolean(string='Reporte completo')

    def _get_data(self):
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        sale = self.env['sale.order'].search([('state','!=','cancel'), ('invoice_ids.payment_state','in',['paid','in_payment'])])
        sales_order_line = self.env['sale.order.line'].search([('order_id.state','!=','cancel')])
        if self.renovations:
            sale = self.env['sale.order'].search([('state','!=','cancel'), ('invoice_ids.payment_state','in',['paid','in_payment']), ('membership_ids.type_contract','=','2')])
            sales_order_line = self.env['sale.order.line'].search([('order_id.state','!=','cancel')])
        if self.complete:
            sale = self.env['sale.order'].search([])
            sales_order_line = self.env['sale.order.line'].search([])
        if self.renovations and self.complete:
            sale = self.env['sale.order'].search([('membership_ids.type_contract','=','2')])
            sales_order_line = self.env['sale.order.line'].search([])

        if self.from_date and self.to_date and self.company_ids:
            sales_order = list(filter(lambda x: x.date_order.astimezone(tz).date() >= self.from_date and x.date_order.astimezone(tz).date() <= self.to_date and x.company_id in self.company_ids, sale))
        elif not self.from_date and self.to_date and self.company_ids:
            sales_order = list(filter(lambda x: x.date_order.astimezone(tz).date() <= self.to_date and x.company_id in self.company_ids, sale))
        elif self.from_date and not self.to_date and self.company_ids:
            sales_order = list(filter(lambda x: x.date_order.astimezone(tz).date() >= self.from_date and x.company_id in self.company_ids, sale))
        elif self.from_date and self.to_date and not self.company_ids:
            sales_order = list(filter(lambda x: x.date_order.astimezone(tz).date() >= self.from_date and x.date_order.astimezone(tz).date() <= self.to_date, sale))
        elif not self.from_date and not self.to_date and self.company_ids:
            sales_order = list(filter(lambda x: x.company_id in self.company_ids, sale))
        elif not self.from_date and self.to_date and not self.company_ids:
            sales_order = list(filter(lambda x: x.date_order.astimezone(tz).date() <= self.to_date, sale))
        elif self.from_date and not self.to_date and not self.company_ids:
            sales_order = list(filter(lambda x: x.date_order.astimezone(tz).date() >= self.from_date, sale))
        else:
            sales_order = sale
        result = []
        users = []
        customers = []
        products = []
        for rec in self.user_ids:
            a = {
                'id': rec,
                'name': rec.name
            }
            users.append(a)
        for rec in self.customer_ids:
            a = {
                'id': rec,
                'name': rec.name
            }
            customers.append(a)
        for rec in self.product_ids:
            a = {
                'id': rec,
                'name': rec.name
            }
            products.append(a)

        margin = 0.0

        if self.type == 'product' and 1 == 0:
            for rec in products:
                for lines in sales_order_line:
                    if lines.product_id == rec['id']:
                        profit = round(lines.product_id.list_price - lines.product_id.standard_price, 2)
                        if lines.product_id.standard_price != 0:
                            margin = round((profit * 100) / lines.product_id.standard_price, 2)
                        res = {
                            'sequence': lines.order_id.name,
                            'date': lines.order_id.date_order,
                            'product_id': lines.product_id,
                            'quantity': lines.product_uom_qty,
                            'cost': lines.product_id.standard_price,
                            'price': lines.product_id.list_price,
                            'profit': profit,
                            'margin': margin,
                            'partner': lines.order_id.partner_id.name,
                            'vat': lines.order_id.partner_id.vat,
                            'discount': lines.discount,
                            'qty_invoiced': lines.qty_invoiced,
                            'document_types': '',
                            'document_names': '',
                            'payment_journals': '',
                        }
                        result.append(res)
        if self.type == 'customer' and 1 == 0:
            for rec in customers:
                for so in sales_order:
                    if so.partner_id == rec['id']:
                        for lines in so.order_line:
                            profit = round(lines.product_id.list_price - lines.product_id.standard_price, 2)
                            if lines.product_id.standard_price != 0:
                                margin = round((profit * 100) / lines.product_id.standard_price, 2)
                            res = {
                                'sequence': so.name,
                                'date': so.date_order,
                                'product': lines.product_id.name,
                                'quantity': lines.product_uom_qty,
                                'cost': lines.product_id.standard_price,
                                'price': lines.product_id.list_price,
                                'profit': profit,
                                'margin': margin,
                                'partner_id': so.partner_id,
                                'partner': so.partner_id.name,
                                'vat': so.partner_id.vat,
                                'discount': lines.discount,
                                'qty_invoiced': lines.qty_invoiced,
                                'document_types': '',
                                'document_names': '',
                                'payment_journals': '',
                            }
                            result.append(res)
        if self.type == 'both' and 1 == 0:
            for rec in customers:
                for p in products:
                    for so in sales_order:
                        if so.partner_id == rec['id']:
                            for lines in so.order_line:
                                if lines.product_id == p['id']:
                                    profit = round(lines.product_id.list_price - lines.product_id.standard_price, 2)
                                    if lines.product_id.standard_price != 0:
                                        margin = round((profit * 100) / lines.product_id.standard_price, 2)
                                    res = {
                                        'sequence': so.name,
                                        'date': so.date_order,
                                        'product': lines.product_id.name,
                                        'quantity': lines.product_uom_qty,
                                        'cost': lines.product_id.standard_price,
                                        'price': lines.product_id.list_price,
                                        'profit': profit,
                                        'margin': margin,
                                        'partner': so.partner_id.name,
                                        'vat': so.partner_id.vat,
                                        'discount': lines.discount,
                                        'qty_invoiced': lines.qty_invoiced,
                                        'document_types': '',
                                        'document_names': '',
                                        'payment_journals': '',
                                    }
                                    result.append(res)
        if self.from_date and self.to_date: #and not self.customer_ids and not self.product_ids:
            for so in sales_order:
                tz = pytz.timezone(self.env.user.tz or 'UTC')
                invoices = so.invoice_ids
                document_types = [invoice.l10n_latam_document_type_id.name for invoice in invoices]
                document_types = ', '.join(x for x in document_types)
                document_names = [invoice.name for invoice in invoices]
                document_names = ', '.join(x for x in document_names)
                reconciled_moves = []
                for invoice in invoices:
                    content = invoice.invoice_payments_widget['content'] if invoice.invoice_payments_widget else []
                    for c in content:
                        reconciled_moves.append(c['move_id'])
                payments = self.env['account.move'].browse(reconciled_moves).mapped('payment_id')
                payment_journals = ', '.join(str(x) for x in [payment.journal_id.name for payment in payments])
                user_id = self.env['hr.department'].search([('company_id','=',so.company_id.id), ('parent_id','=',False)], limit=1).manager_id.user_id
                for lines in so.order_line:
                    profit = round(lines.product_id.list_price - lines.product_id.standard_price, 2)
                    if lines.product_id.standard_price != 0:
                        margin = round((profit * 100) / lines.product_id.standard_price, 2)
                    res = {
                        'sequence': so.name,
                        'date': so.date_order.astimezone(tz),
                        'product': lines.product_id.name,
                        'quantity': lines.product_uom_qty,
                        'cost': lines.product_id.standard_price,
                        'price': lines.product_id.list_price,
                        'price_invoiced' : lines.qty_invoiced * lines.product_id.list_price,
                        'profit': profit,
                        'margin': margin,
                        'partner': so.partner_id.name,
                        'vat': so.partner_id.vat,
                        'discount': lines.discount,
                        'document_types': document_types,
                        'document_names': document_names,
                        'payment_journals': payment_journals,
                        'amount_cash': sum(payments.filtered(lambda x: x.journal_id.type == 'cash').mapped('amount')),
                        'amount_bank': sum(payments.filtered(lambda x: x.journal_id.type == 'bank').mapped('amount')),
                        'manager_id': user_id.name,
                        'user_id': so.user_id.name if so.user_id else '',
                        'date_invoice': invoices[0].invoice_date if invoices else '',
                    }
                    result.append(res)

        datas = {
            'ids': self,
            'model': 'sale.report.advance',
            'form': result,
            'partner_id': customers,
            'product_id': products,
            'start_date': self.from_date,
            'end_date': self.to_date,
            'type': self.type,
            'no_value': False,

        }
        if self.from_date and self.to_date and not self.customer_ids and not self.product_ids:
            datas['no_value']=True
        return datas

    def get_report(self):
        datas = self._get_data()
        return self.env.ref('sale_report_advanced.action_sale_report').report_action([], data=datas)

    def get_excel_report(self):
        datas = self._get_data()
        return {
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'data': {'model': 'sale.report.advance',
                     'output_format': 'xlsx',
                     'options': json.dumps(datas, default=date_utils.json_default),
                     'report_name': 'Excel Report Name',
                     },
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('VENTAS')
        record = []
        # cell_format = workbook.add_format({'font_size': '12px'})
        # head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '20px'})
        # txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
        # format1 = workbook.add_format({'font_size': 10, 'align': 'center','bg_color':'#bbd5fc','border': 1})
        # format2 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True,'bg_color': '#6BA6FE', 'border': 1})
        # format4 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True,'border': 1})
        # format3 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True, 'bg_color': '#c0dbfa', 'border': 1})
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'valign': 'vcenter', 'bold': True})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format22 = workbook.add_format({'font_size': 10, 'align': 'right', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center', 'valign': 'vcenter'})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right', 'valign': 'vcenter'})
        monetary_size_8_r = workbook.add_format({'num_format': '"S/." #,##0.00', 'font_size': 8, 'align': 'right', 'valign': 'vcenter'})
        
        # sheet.merge_range('G2:N3', 'Sales Profit Report', cell_format)
        # if data['start_date'] and data['end_date']:
        #     sheet.write('G6', 'From:', cell_format)
        #     sheet.merge_range('H6:I6', data['start_date'], txt)
        #     sheet.write('L6', 'To:', cell_format)
        #     sheet.merge_range('M6:N6', data['end_date'], txt)
        # if data['type'] == 'product':
        #     record = data['product_id']
        # if data['type'] == 'customer':
        #     record = data['partner_id']
            
        sheet.merge_range('A2:P2', 'DETALLE DE VENTAS', format0)
        if data['start_date'] and data['end_date']:
            sheet.write('A4', 'Desde:', format4)
            sheet.merge_range('B4:C4', data['start_date'], format21)
            sheet.write('F4', 'Hasta:', format4)
            sheet.merge_range('G4:H4', data['end_date'], format21)
        if data['type'] == 'product':
            record = data['product_id']
        if data['type'] == 'customer':
            record = data['partner_id']
        h_row = 7
        h_col = 9
        count = 0
        row = 5
        col = 0
        row_number = 5
        t_row = 6
        if 1 == 1:
            row += 1
            row_number += 2
            t_qty = 0
            t_cost = 0
            t_price = 0
            t_subtotal = 0
            t_profit = 0
            t_margin = 0
            t_cash = 0
            t_bank = 0
            t_col = 4
            sheet.write(row, col, 'Order', format21)
            col += 1
            sheet.write(row, col, 'DNI', format21)
            col += 1
            sheet.write(row, col, 'Cliente', format21)
            sheet.set_column('C:C', 20)
            col += 1
            sheet.write(row, col, 'Fecha', format21)
            sheet.set_column('D:D', 15)
            col += 1
            sheet.write(row, col, 'Producto', format21)
            sheet.set_column('E:E', 20)
            col += 1
            sheet.write(row, col, 'Cantidad', format21)
            col += 1
            # sheet.write(row, col, 'Costo', format21)
            # col += 1
            sheet.write(row, col, 'Precio', format21)
            col += 1
            sheet.write(row, col, 'Importe', format21)
            col += 1
            # sheet.write(row, col, 'Beneficio', format21)
            # col += 1    
            # sheet.write(row, col, 'Margen', format21)
            # col += 1
            sheet.write(row, col, 'Descuento', format21)
            col += 1
            sheet.write(row, col, 'Tipo de Comprobante', format21)
            sheet.set_column('J:J', 20)
            col += 1
            sheet.write(row, col, 'Número de Comprobante', format21)
            sheet.set_column('K:K', 20)
            col += 1
            sheet.write(row, col, 'Diarios de Pago', format21)
            sheet.set_column('L:L', 15)
            col += 1
            sheet.write(row, col, 'Total Efectivo', format21)
            sheet.set_column('M:M', 12)
            col += 1
            sheet.write(row, col, 'Total Banco', format21)
            sheet.set_column('N:N', 12)
            col += 1
            sheet.write(row, col, 'Responsable', format21)
            sheet.set_column('O:O', 15)
            col += 1
            sheet.write(row, col, 'Vendedor', format21)
            sheet.set_column('P:P', 15)
            col += 1
            sheet.write(row, col, 'Fecha Factura', format21)
            sheet.set_column('Q:Q', 12)
            col += 1

            inv_list = []
            amount_cash1 = 0
            amount_bank1 = 0  
            for val in data['form']:
                column_number = 0
                sheet.write(row_number, column_number, val['sequence'], font_size_8)
                column_number += 1
                sheet.write(row_number, column_number, val['vat'], font_size_8)
                column_number += 1
                sheet.write(row_number, column_number, val['partner'], font_size_8)
                column_number += 1
                sheet.write(row_number, column_number, val['date'], font_size_8)
                column_number += 1
                sheet.write(row_number, column_number, val['product'], font_size_8)
                column_number += 1
                sheet.write(row_number, column_number, val['quantity'], font_size_8_r)
                t_qty += val['quantity']
                column_number += 1
                # sheet.write(row_number, column_number, val['cost'], monetary_size_8_r)
                # t_cost += val['cost']
                # column_number += 1
                sheet.write(row_number, column_number, val['price'], monetary_size_8_r)
                t_price += val['price']
                column_number += 1
                sheet.write(row_number, column_number, val['price_invoiced'], monetary_size_8_r)
                t_subtotal += val['price_invoiced']
                column_number += 1
                # sheet.write(row_number, column_number, val['profit'], monetary_size_8_r)
                # t_profit += val['profit']
                # column_number += 1
                # sheet.write(row_number, column_number, val['margin'], monetary_size_8_r)
                # t_margin += val['margin']
                # column_number += 1
                sheet.write(row_number, column_number, val['discount'], font_size_8_r)
                column_number += 1
                sheet.write(row_number, column_number, val['document_types'], font_size_8)
                column_number += 1
                sheet.write(row_number, column_number, val['document_names'], font_size_8)
                column_number += 1
                sheet.write(row_number, column_number, val['payment_journals'], font_size_8)
                column_number += 1

                amount_cash1 = 0
                amount_bank1 = 0
                if val['sequence'] not in inv_list:
                    amount_cash1 = val['amount_cash']
                    amount_bank1 = val['amount_bank']
                sheet.write(row_number, column_number, amount_cash1, monetary_size_8_r)
                t_cash += amount_cash1
                column_number += 1
                sheet.write(row_number, column_number, amount_bank1, monetary_size_8_r)
                t_bank += amount_bank1
                column_number += 1

                #sheet.write(row_number, column_number, val['amount_cash'], monetary_size_8_r)
                #t_cash += val['amount_cash']
                #column_number += 1
                #sheet.write(row_number, column_number, val['amount_bank'], monetary_size_8_r)
                #t_bank += val['amount_bank']
                #column_number += 1

                sheet.write(row_number, column_number, val['manager_id'], font_size_8)
                column_number += 1
                sheet.write(row_number, column_number, val['user_id'], font_size_8)
                column_number += 1
                sheet.write(row_number, column_number, val['date_invoice'], font_size_8)
                column_number += 1
                row_number += 1
                inv_list.append(val['sequence'])

            sheet.write(row_number, t_col, 'Total', format4)
            t_col += 1
            sheet.write(row_number, t_col, t_qty, format22)
            t_col += 1
            # sheet.write(row_number, t_col, t_cost, format4)
            # t_col += 1
            sheet.write(row_number, t_col, t_price, format22)
            t_col += 1
            sheet.write(row_number, t_col, t_subtotal, format22)
            t_col += 5
            # sheet.write(row_number, t_col, t_profit, format4)
            # t_col += 1
            # sheet.write(row_number, t_col, t_margin, format4)
            # t_col += 1
            sheet.write(row_number, t_col, t_cash, format22)
            t_col += 1
            sheet.write(row_number, t_col, t_bank, format22)
            t_col += 1

        # if data['type'] == 'product' or data['type'] == 'customer':
        #     for rec in record:
        #         sheet.merge_range(h_row, h_col-3,h_row,h_col+4,rec['name'], format3)
        #         row = row + count + 3
        #         sheet.write(row, col, 'Order', format2)
        #         col += 1
        #         sheet.write(row, col, 'Date', format2)
        #         sheet.set_column('H:H', 15)
        #         col += 1
        #         if data['type'] == 'product':
        #             sheet.write(row, col, 'Customer', format2)
        #             sheet.set_column('I:I', 20)
        #             col += 1
        #         elif data['type'] == 'customer':
        #             sheet.write(row, col, 'Product', format2)
        #             sheet.set_column('I:I', 20)
        #             col += 1
        #         sheet.write(row, col, 'Quantity', format2)
        #         col += 1
        #         sheet.write(row, col, 'Cost', format2)
        #         col += 1
        #         sheet.write(row, col, 'Price', format2)
        #         col += 1
        #         sheet.write(row, col, 'Profit', format2)
        #         col += 1
        #         sheet.write(row, col, 'Margin(%)', format2)
        #         col += 1
        #         col = 6
        #         count = 0
        #         row_number = row_number + count + 3
        #         t_qty = 0
        #         t_cost = 0
        #         t_price = 0
        #         t_profit = 0
        #         t_margin = 0
        #         t_col = 8
        #         for val in data['form']:
        #             if data['type'] == 'customer':
        #                 if val['partner_id'] == rec['id']:
        #                     count += 1
        #                     column_number = 6
        #                     sheet.write(row_number, column_number, val['sequence'], format1)
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['date'], format1)
        #                     sheet.set_column('H:H', 15)
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['product'], format1)
        #                     sheet.set_column('I:I', 20)
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['quantity'], format1)
        #                     t_qty += val['quantity']
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['cost'], format1)
        #                     t_cost += val['cost']
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['price'], format1)
        #                     t_price += val['price']
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['profit'], format1)
        #                     t_profit += val['profit']
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['margin'], format1)
        #                     t_margin += val['margin']
        #                     column_number += 1
        #                     row_number += 1
        #             if data['type'] == 'product':
        #                 if val['product_id'] == rec['id']:
        #                     count += 1
        #                     column_number = 6
        #                     sheet.write(row_number, column_number, val['sequence'], format1)
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['date'], format1)
        #                     sheet.set_column('H:H', 15)
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['partner'], format1)
        #                     sheet.set_column('I:I', 20)
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['quantity'], format1)
        #                     t_qty += val['quantity']
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['cost'], format1)
        #                     t_cost += val['cost']
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['price'], format1)
        #                     t_price += val['price']
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['profit'], format1)
        #                     t_profit += val['profit']
        #                     column_number += 1
        #                     sheet.write(row_number, column_number, val['margin'], format1)
        #                     t_margin += val['margin']
        #                     column_number += 1
        #                     row_number += 1
        #         t_row = t_row + count + 3
        #         sheet.write(t_row, t_col, 'Total', format4)
        #         t_col += 1
        #         sheet.write(t_row, t_col, t_qty, format4)
        #         t_col += 1
        #         sheet.write(t_row, t_col, t_cost, format4)
        #         t_col += 1
        #         sheet.write(t_row, t_col, t_price, format4)
        #         t_col += 1
        #         sheet.write(t_row, t_col, t_profit, format4)
        #         t_col += 1
        #         sheet.write(t_row, t_col, t_margin, format4)
        #         t_col += 1
        #         h_row = h_row + count + 3
        # if data['type'] == 'both' or data['no_value'] == True:
        #     row += 3
        #     row_number += 2
        #     t_qty = 0
        #     t_cost = 0
        #     t_price = 0
        #     t_profit = 0
        #     t_margin = 0
        #     t_col = 9
        #     sheet.write(row, col, 'Order', format2)
        #     col += 1
        #     sheet.write(row, col, 'Date', format2)
        #     sheet.set_column('H:H', 15)
        #     col += 1
        #     sheet.write(row, col, 'Customer', format2)
        #     sheet.set_column('I:I', 20)
        #     col += 1
        #     sheet.write(row, col, 'Product', format2)
        #     sheet.set_column('J:J', 20)
        #     col += 1
        #     sheet.write(row, col, 'Quantity', format2)
        #     col += 1
        #     sheet.write(row, col, 'Cost', format2)
        #     col += 1
        #     sheet.write(row, col, 'Price', format2)
        #     col += 1
        #     sheet.write(row, col, 'Profit', format2)
        #     col += 1
        #     sheet.write(row, col, 'Margin', format2)
        #     col += 1
        #     row_number+=1
        #     for val in data['form']:
        #         column_number = 6
        #         sheet.write(row_number, column_number, val['sequence'], format1)
        #         column_number += 1
        #         sheet.write(row_number, column_number, val['date'], format1)
        #         sheet.set_column('H:H', 15)
        #         column_number += 1
        #         sheet.write(row_number, column_number, val['partner'], format1)
        #         sheet.set_column('I:I', 20)
        #         column_number += 1
        #         sheet.write(row_number, column_number, val['product'], format1)
        #         sheet.set_column('J:J', 20)
        #         column_number += 1
        #         sheet.write(row_number, column_number, val['quantity'], format1)
        #         t_qty += val['quantity']
        #         column_number += 1
        #         sheet.write(row_number, column_number, val['cost'], format1)
        #         t_cost += val['cost']
        #         column_number += 1
        #         sheet.write(row_number, column_number, val['price'], format1)
        #         t_price += val['price']
        #         column_number += 1
        #         sheet.write(row_number, column_number, val['profit'], format1)
        #         t_profit += val['profit']
        #         column_number += 1
        #         sheet.write(row_number, column_number, val['margin'], format1)
        #         t_margin += val['margin']
        #         column_number += 1
        #         row_number += 1
        #     sheet.write(row_number, t_col, 'Total', format4)
        #     t_col += 1
        #     sheet.write(row_number, t_col, t_qty, format4)
        #     t_col += 1
        #     sheet.write(row_number, t_col, t_cost, format4)
        #     t_col += 1
        #     sheet.write(row_number, t_col, t_price, format4)
        #     t_col += 1
        #     sheet.write(row_number, t_col, t_profit, format4)
        #     t_col += 1
        #     sheet.write(row_number, t_col, t_margin, format4)
        #     t_col += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
