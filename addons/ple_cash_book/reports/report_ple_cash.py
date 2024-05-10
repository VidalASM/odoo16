from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class CashReport(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content_excel(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        style_column = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
            'border': 7
        })
        style_content = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'border': 7
        })
        style_number = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
            'border': 7
        })
        style_date = workbook.add_format({
            'size': 10,
            'num_format': 'dd/mm/yy',
            'border': 7
        })

        ws = workbook.add_worksheet('1.1 LIBRO CAJA Y BANCOS - DETALLE DE LOS MOVIMIENTOS DEL EFECTIVO')
        ws.set_column('A:A', 15)
        ws.set_column('B:B', 40)
        ws.set_column('C:C', 40)
        ws.set_column('D:D', 40)
        ws.set_column('E:E', 40)
        ws.set_column('F:F', 40)
        ws.set_column('G:G', 40)
        ws.set_column('H:H', 40)
        ws.set_column('I:I', 40)
        ws.set_column('J:J', 40)
        ws.set_column('K:K', 40)
        ws.set_column('L:L', 40)
        ws.set_column('M:M', 40)
        ws.set_column('N:N', 40)
        ws.set_column('O:O', 40)
        ws.set_column('P:P', 40)
        ws.set_column('Q:Q', 40)
        ws.set_column('R:R', 40)

        ws.set_row(0, 50)

        ws.write(0, 0, 'Periodo', style_column)
        ws.write(0, 1, 'CUO', style_column)
        ws.write(0, 2, 'Número correlativo del asiento', style_column)
        ws.write(0, 3, 'Código Cuenta Contable', style_column)
        ws.write(0, 4, 'Código de la unidad de Operación', style_column)
        ws.write(0, 5, 'Código Centro de Costos', style_column)
        ws.write(0, 6, 'Tipo de Moneda Origen', style_column)
        ws.write(0, 7, 'Tipo de comprobante de pago', style_column)
        ws.write(0, 8, 'Número serie del comprobante de pago', style_column)
        ws.write(0, 9, 'Número del comprobante de pago', style_column)
        ws.write(0, 10, 'Fecha contable', style_column)
        ws.write(0, 11, 'Fecha de Vencimiento', style_column)
        ws.write(0, 12, 'Fecha de la operación o emisión', style_column)
        ws.write(0, 13, 'Glosa de la operación registrada', style_column)
        ws.write(0, 14, 'Glosa referencial', style_column)
        ws.write(0, 15, 'Debe', style_column)
        ws.write(0, 16, 'Haber', style_column)
        ws.write(0, 17, 'Dato estructurado', style_column)
        ws.write(0, 18, 'Estado de la operación', style_column)

        i = 1
        for value in self.data:
            ws.write(i, 0, value['period'], style_content)
            ws.write(i, 1, value['cuo'], style_content)
            ws.write(i, 2, value['correlative'], style_content)
            ws.write(i, 3, value['account_code'], style_content)
            ws.write(i, 4, value['unit_operation_code'], style_content)
            ws.write(i, 5, value['cost_center_code'], style_content)
            ws.write(i, 6, value['currency_name'], style_content)
            ws.write(i, 7, value['type_payment_document'], style_content)
            ws.write(i, 8, value['serie'], style_content)
            ws.write(i, 9, value['document_number'], style_content)
            ws.write(i, 10, value['accounting_date'], style_date)
            ws.write(i, 11, value['date_due'], style_date)
            ws.write(i, 12, value['operation_date'], style_date)
            ws.write(i, 13, value['gloss'], style_content)
            ws.write(i, 14, value['referential_gloss'], style_content)
            ws.write(i, 15, value['debit'], style_number)
            ws.write(i, 16, value['credit'], style_number)
            ws.write(i, 17, value['data_structured'], style_content)
            ws.write(i, 18, value['state'], style_content)
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self, file_type):
        year, month = self.obj.date_start.strftime('%Y/%m').split('/')
        if file_type == 'xlsx':
            filename_report = 'Libro Caja_{company_name}_{period_year}{period_month}.{file_type}'.format(
                company_name=self.obj.company_id.name,
                period_year=year,
                period_month=month,
                file_type=file_type
            )
        else:
            filename_report = 'LE{vat}{period_year}{period_month}0001010000{state_send}{has_info}11.{file_type}'.format(
                vat=self.obj.company_id.vat,
                period_year=year,
                period_month=month,
                state_send=self.obj.state_send or '',
                has_info=int(bool(self.data)),
                file_type=file_type
            )
        return filename_report

    def get_content_txt(self):
        raw = ''
        template = '{period}|{cuo}|{correlative}|{account_code}|' \
                   '{unit_operation_code}|{cost_center_code}|{currency_name}|{type_payment_document}|' \
                   '{serie}|{document_number}|{accounting_date}|{date_due}|' \
                   '{operation_date}|{gloss}|{referential_gloss}|{debit}|' \
                   '{credit}|{data_structured}|{state}|\r\n'

        for value in self.data:
            raw += template.format(
                period=value['period'],
                cuo=value['cuo'],
                correlative=value['correlative'],
                account_code=value['account_code'],
                unit_operation_code=value['unit_operation_code'],

                cost_center_code=value['cost_center_code'],
                currency_name=value['currency_name'],
                type_payment_document=value['type_payment_document'],
                serie=value['serie'],
                document_number=value['document_number'],

                accounting_date=value['accounting_date'],
                date_due=value['date_due'],
                operation_date=value['operation_date'],
                gloss=value['gloss'],
                referential_gloss=value['referential_gloss'],

                debit=value['debit'],
                credit=value['credit'],
                data_structured=value['data_structured'],
                state=value['state']
            )
        return raw
