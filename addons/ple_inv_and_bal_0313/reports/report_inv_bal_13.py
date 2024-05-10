from io import BytesIO
from datetime import date

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportInvBal13Excel(object):

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
        number_format = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
        })
        date_format = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'num_format': 'dd/mm/yy',
        })

        ws = workbook.add_worksheet('Report CXC Empresa')

        ws.set_column('A:A', 12)
        ws.set_column('B:B', 18)
        ws.set_column('C:C', 18)
        ws.set_column('D:D', 30)
        ws.set_column('E:E', 32)
        ws.set_column('F:F', 39)
        ws.set_column('G:G', 54)
        ws.set_column('H:H', 32)
        ws.set_column('I:I', 30)
        ws.set_column('J:J', 28)
        ws.set_column('K:K', 28)
        ws.set_row(0, 50)

        ws.write(0, 0, 'Periodo', style1)
        ws.write(0, 1, 'CUO', style1)
        ws.write(0, 2, 'Numero correlativo', style1)
        ws.write(0, 3, 'Tipo de documento del tercero', style1)
        ws.write(0, 4, 'Número de documento del tercero', style1)
        ws.write(0, 5, 'Fecha de emisión del comprobante de pago', style1)
        ws.write(0, 6, 'Apellidos y nombres del tercero', style1)
        ws.write(0, 7, 'Código de la cuenta contable asociada', style1)
        ws.write(0, 8, 'Monto pendiente de pago al tercero', style1)
        ws.write(0, 9, 'Estado de la operación', style1)
        ws.write(0, 10, 'Campo de libre utilización', style1)

        data = []

        for i in range(len(self.data_1)):
            join = {**self.data_1[i]}
            data.append(join)
        i = 1
        for values in data:
            name_document_string = ''.join(char for char in values['document_name'] if char.isalnum())
            ws.write(i, 0, values['name'], style3)
            ws.write(i, 1, name_document_string, style3)
            ws.write(i, 2, values['correlative'], style3)
            ws.write(i, 3, values['type_document_third'], style3)
            ws.write(i, 4, values['tax_identification_number'], style3)
            ws.write(i, 5, date.strftime(values['date_issue'], '%d/%m/%Y') if values['date_issue'] else '', date_format)
            ws.write(i, 6, values['business_name'], style3)
            ws.write(i, 7, values['code'], style3)
            ws.write(i, 8, values['provision_amount'], number_format)
            ws.write(i, 9, '1', style3)
            ws.write(i, 10, '', style3)
            i += 1

        workbook.close()
        output.seek(0)

        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Cuentas_por_pagar_diversas_{}.xlsx'.format(year_month)


class ReportInvBal13Txt(object):

    def __init__(self, obj, data_1):
        self.obj = obj
        self.data_1 = data_1

    def get_content(self):
        raw = ''
        template = '{name}|{accounting_seat}|{correlative}|{type_document_third}|{tax_identification_number}|' \
                   '{date_issue}|{business_name}|{code}|{provision_amount}|{account_status}|\r\n'

        data = []
        for i in range(len(self.data_1)):
            join = {**self.data_1[i]}
            data.append(join)

        for value in data:
            name_document_string = ''.join(char for char in value['document_name'] if char.isalnum())
            raw += template.format(
                name= value['name'],
                accounting_seat= name_document_string,
                correlative=  value['correlative'],
                type_document_third= value['type_document_third'],
                tax_identification_number=  value['tax_identification_number'],
                date_issue= date.strftime(value['date_issue'], '%d/%m/%Y') if value['date_issue'] else '',
                business_name = value['business_name'],
                code=value['code'],
                provision_amount = "{:.2f}".format(float(value['provision_amount'])) if value['provision_amount'] else '',
                account_status="1"
            )
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}031300{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year= year,
            period_month = month,
            period_day = day,
            eeff_oportunity = self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data_1))
        )
