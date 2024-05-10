from io import BytesIO
import re
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportInvBal15Excel(object):

    def __init__(self, obj, data_1):
        self.obj = obj
        self.data_1 = data_1

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        style1 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
            'border': 7
        })
        style3 = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'font_name': 'Arial'
        })
        content_number_format = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
        })

        ws = workbook.add_worksheet('Report CXC Empresa')

        ws.set_column('A:A', 12)
        ws.set_column('B:B', 18)
        ws.set_column('C:C', 18)
        ws.set_column('D:D', 38)
        ws.set_column('E:E', 36)
        ws.set_column('F:F', 39)
        ws.set_column('G:G', 32)
        ws.set_column('H:H', 32)
        ws.set_column('I:I', 18)
        ws.set_column('J:J', 18)
        ws.set_column('K:K', 18)
        ws.set_column('L:L', 24)
        ws.set_column('M:M', 28)
        ws.set_row(0, 50)

        ws.write(0, 0, 'Periodo', style1)
        ws.write(0, 1, 'CUO', style1)
        ws.write(0, 2, 'Numero Correlativo', style1)
        ws.write(0, 3, 'Tipo de Comprobante de Pago Relacionado', style1)
        ws.write(0, 4, 'Número Serie del Comprobante de Pago', style1)
        ws.write(0, 5, 'Número del Comprobante de Pago Relacionado', style1)
        ws.write(0, 6, 'Código de la Cuenta Contable Asociada', style1)
        ws.write(0, 7, 'Concepto o Descripción de la Operación', style1)
        ws.write(0, 8, 'Saldo Final', style1)
        ws.write(0, 9, 'Adiciones', style1)
        ws.write(0, 10, 'Deducciones', style1)
        ws.write(0, 11, 'Estado de la operación', style1)
        ws.write(0, 12, 'Campo de libre utilización', style1)

        data = []

        for i in range(len(self.data_1)):
            join = {**self.data_1[i]}
            data.append(join)

        i = 1

        adi = '0.00'
        sub = '0.00'
        for value in data:
            name_document_string = ''.join(char for char in value['document_name'] if char.isalnum())

            ws.write(i, 0, value['name'], style3)
            ws.write(i, 1, name_document_string, style3)
            ws.write(i, 2, value['correlative'], style3)
            ws.write(i, 3, value['type_l10n_latam_identification'], style3)
            ws.write(i, 4, value['serial_number_payment'], style3)
            ws.write(i, 5, value['related_payment_voucher'], style3)
            ws.write(i, 6, re.sub(r"[^a-zA-Z0-9]", "", value['code']), style3)
            ws.write(i, 7, value['ref'], style3)
            ws.write(i, 8, value['outstanding_balance'] if adi == '0.00' and sub == '0.00' else '0.00',
                     content_number_format)
            ws.write(i, 9, adi, content_number_format)
            ws.write(i, 10, sub, content_number_format)
            ws.write(i, 11, '1', style3)
            ws.write(i, 12, '', style3)
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Activos_Pasivos_Diferidos_{}.xlsx'.format(year_month)


class ReportInvBal15Txt(object):

    def __init__(self, obj, data_1):
        self.obj = obj
        self.data_1 = data_1

    def get_content(self):
        raw = ''
        template = '{name}|{accounting_seat}|{correlative}|{type_l10n_latam_identification}|{serial_number_payment}|' \
                   '{related_payment_voucher}|{code}|{ref}|{outstanding_balance}|{additions}|{deductions}|' \
                   '{account_status}|\r\n'

        data = []
        for i in range(len(self.data_1)):
            join = {**self.data_1[i]}
            data.append(join)

        adi = '0.00'
        sub = '0.00'
        for value in data:
            name_document_string = ''.join(char for char in value['document_name'] if char.isalnum())

            raw += template.format(
                name = value['name'],
                accounting_seat = name_document_string,
                correlative = value['correlative'],
                type_l10n_latam_identification = value['type_l10n_latam_identification'],
                serial_number_payment = value['serial_number_payment'],
                related_payment_voucher = value['related_payment_voucher'],
                code = re.sub(r"[^a-zA-Z0-9]", "", value['code']),
                ref = value['ref'],
                outstanding_balance= "{:.2f}".format(float(value['outstanding_balance'])),
                additions=adi,
                deductions=sub,
                account_status="1"
            )
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}031500{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data_1))
        )
