from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportInvBal20Excel(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        style1 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
            'font_name': 'Arial',
            'border': 7
        })
        style_number = workbook.add_format({
            'size': 11,
            'num_format': '#,##0.00',
        })

        ws = workbook.add_worksheet('F3.20 Est Gan y Perd Fun')

        ws.set_column('A:A', 10)
        ws.set_column('B:B', 28)
        ws.set_column('C:C', 45)
        ws.set_column('D:D', 50)
        ws.set_column('E:E', 28)
        ws.set_column('F:F', 34)
        ws.set_row(0, 50)

        ws.write(0, 0, 'Periodo', style1)
        ws.write(0, 1, 'Código del catálogo', style1)
        ws.write(0, 2, 'Código del Rubro del Estado Financiero', style1)
        ws.write(0, 3, 'Nombre de la cuenta contable', style1)
        ws.write(0, 4, 'Saldo del Rubro Contable', style1)
        ws.write(0, 5, 'Indica el estado de la operación', style1)

        i = 1
        for value in self.data:
            ws.write(i, 0, value['name'])
            ws.write(i, 1, value['catalog_code'])
            ws.write(i, 2, value['financial_state_code'])
            ws.write(i, 3, value['description'])
            ws.write(i, 4, value['real_credit'] * -1, style_number)
            ws.write(i, 5, value['state'])
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Estado de Resultados_{}.xlsx'.format(year_month)


class ReportInvBal20Txt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        raw = ''
        template = '{name}|{catalog_code}|{financial_state_code}|{credit}|{state}|\r\n'

        for value in self.data:
            raw += template.format(
                name=value['name'],
                catalog_code=value['catalog_code'],
                financial_state_code=value['financial_state_code'],
                credit="{:.2f}".format(value['real_credit'] * -1),
                state=value['state'],
            )
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}032000{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data))
        )
