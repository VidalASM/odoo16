from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class BankReport(object):

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

        ws = workbook.add_worksheet('1.2 LIBRO CAJA Y BANCOS - DETALLE DE LOS MOVIMIENTOS DE LA CUENTA CORRIENTE')
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
        ws.set_column('S:S', 40)
        ws.set_column('T:T', 40)
        ws.set_column('U:U', 40)

        ws.set_row(0, 50)

        ws.write(0, 0, 'Periodo', style_column)
        ws.write(0, 1, 'CUO', style_column)
        ws.write(0, 2, 'Número correlativo del asiento', style_column)
        ws.write(0, 3, 'Código de la entidad financiera', style_column)
        ws.write(0, 4, 'Código de la cuenta bancaria', style_column)
        ws.write(0, 5, 'Fecha de la operación', style_column)
        ws.write(0, 6, 'Medio de pago', style_column)
        ws.write(0, 7, 'Descripción de la operación bancaria', style_column)
        ws.write(0, 8, 'Tipo de documento girador', style_column)
        ws.write(0, 9, 'Número de documento girador', style_column)
        ws.write(0, 10, 'Nombre completo girador', style_column)
        ws.write(0, 11, 'Número de transacción bancaria', style_column)
        ws.write(0, 12, 'Debe', style_column)
        ws.write(0, 13, 'Haber', style_column)
        ws.write(0, 14, 'Estado de la operación', style_column)

        i = 1
        for value in self.data:
            ws.write(i, 0, value['period'], style_content)
            ws.write(i, 1, value['cuo'], style_content)
            ws.write(i, 2, value['correlative'], style_content)
            ws.write(i, 3, value['bank_code'], style_content)
            ws.write(i, 4, value['account_bank_code'], style_content)
            ws.write(i, 5, value['date'], style_content)
            ws.write(i, 6, value['payment_method'], style_content)
            ws.write(i, 7, value['operation_description'], style_content)
            ws.write(i, 8, value['partner_type_document'], style_content)
            ws.write(i, 9, value['partner_document_number'], style_content)
            ws.write(i, 10, value['partner_name'], style_date)
            ws.write(i, 11, value['transaction_number'], style_date)
            ws.write(i, 12, value['debit'], style_number)
            ws.write(i, 13, value['credit'], style_number)
            ws.write(i, 14, value['state'], style_content)
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self, file_type):
        year, month = self.obj.date_start.strftime('%Y/%m').split('/')
        if file_type == 'xlsx':
            filename_report = 'Libro Bancos_{company_name}_{period_year}{period_month}.{file_type}'.format(
                company_name=self.obj.company_id.name,
                period_year=year,
                period_month=month,
                file_type=file_type
            )
        else:
            filename_report = 'LE{vat}{period_year}{period_month}0001020000{state_send}{has_info}11.{file_type}'.format(
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
        template = '{period}|{cuo}|{correlative}|{bank_code}|' \
                   '{account_bank_code}|{date}|{payment_method}|{operation_description}|' \
                   '{partner_type_document}|{partner_document_number}|{partner_name}|{transaction_number}|' \
                   '{debit}|{credit}|{state}|\r\n'

        for value in self.data:
            raw += template.format(
                period=value['period'],
                cuo=value['cuo'],
                correlative=value['correlative'],
                bank_code=value['bank_code'],
                account_bank_code=value['account_bank_code'],
                date=value['date'],
                payment_method=value['payment_method'],
                operation_description=value['operation_description'],
                partner_type_document=value['partner_type_document'],
                partner_document_number=value['partner_document_number'],
                partner_name=value['partner_name'],
                transaction_number=value['transaction_number'],
                debit=value['debit'],
                credit=value['credit'],
                state=value['state']
            )
        return raw
