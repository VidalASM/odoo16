from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportInvBalEightExcel(object):

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
            'font_name': 'Arial'
        })
        style_number = workbook.add_format({
            'size': 11,
            'num_format': '0.00',
        })

        ws = workbook.add_worksheet('Report CXC Empresa')
        ws.set_column('A:H', 15)

        ws.set_row(0, 50)

        ws.write(0, 0, 'Periodo', style1)
        ws.write(0, 1, 'CUO', style1)
        ws.write(0, 2, 'Numero Correlativo', style1)
        ws.write(0, 3, 'Tipo de documento del emisor', style1)
        ws.write(0, 4, 'Número de documento del emisor', style1)
        ws.write(0, 5, 'Apellidos y Nombres, Den. o Raz. Social Emisor', style1)
        ws.write(0, 6, 'Código del titulo', style1)
        ws.write(0, 7, 'Valor nominal unitario del titulo', style1)
        ws.write(0, 8, 'Cantidad de títulos', style1)
        ws.write(0, 9, 'Valor en libros - Costo total de los títulos', style1)
        ws.write(0, 10, 'Valor en libros - Provisión total de los títulos', style1)
        ws.write(0, 11, 'Indica el estado de la operación', style1)
        ws.write(0, 12, 'Campos de libre utilización.', style1)

        data = []

        for i in range(len(self.data_1)):
            join = {**self.data_1[i]}
            data.append(join)
        i = 1
        for value in data:
            name_document_string = ''.join(char for char in value['document_name'] if char.isalnum())

            ws.write(i, 0, value['name'])
            ws.write(i, 1, name_document_string),
            ws.write(i, 2, value['correlative'])
            ws.write(i, 3, value['type_document_transmitter'])
            ws.write(i, 4, value['number_document_transmitter'])
            ws.write(i, 5, value['transmitter_name'])
            ws.write(i, 6, value['title_code'])
            ws.write(i, 7, value['title_unit_value'], style_number)
            ws.write(i, 8, value['total_amount_value'])
            ws.write(i, 9, value['total_title_costs'], style_number)
            ws.write(i, 10, value['total_title_provision'], style_number)
            ws.write(i, 11, '1')
            ws.write(i, 12, '|')
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Inversiones Mobiliarias_{}.xlsx'.format(year_month)


class ReportInvBalEightTxt(object):

    def __init__(self, obj, data_1):
        self.obj = obj
        self.data_1 = data_1

    def get_content(self):
        raw = ''
        template = '{name}|{name_document_string}|{correlative}|{type_document_transmitter}|{number_document_transmitter}' \
                   '|{transmitter_name}|{title_code}|{title_unit_value}|{total_amount_value}|{total_title_costs}|' \
                   '{total_title_provision}|{operation_status}|{free_field}\r\n'

        data = []
        for i in range(len(self.data_1)):
            join = {**self.data_1[i]}
            data.append(join)
        for value in data:
            name_document_string = ''.join(char for char in value['document_name'] if char.isalnum())
            raw += template.format(
                name=value['name'],
                name_document_string=name_document_string,
                correlative=value['correlative'],
                type_document_transmitter=value['type_document_transmitter'],
                number_document_transmitter=value['number_document_transmitter'],
                transmitter_name=value['transmitter_name'],
                title_code=value['title_code'],
                title_unit_value="{:.2f}".format((value['title_unit_value'])),
                total_amount_value=value['total_amount_value'],
                total_title_costs="{:.2f}".format(value['total_title_costs']),
                total_title_provision="{:.2f}".format(float(value['total_title_provision'])),
                operation_status="1",
                free_field="|"
            )

        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}030800{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data_1))
        )
