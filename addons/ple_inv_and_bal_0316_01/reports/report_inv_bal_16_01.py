from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportInvBalSixteenExcel(object):

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
            'font_name': 'Arial'
        })
        style_number = workbook.add_format({
            'size': 11,
            'num_format': '#,##0.00',
        })

        ws = workbook.add_worksheet('Report CXC Empresa')
        ws.set_column('A:H', 15)

        ws.set_row(0, 50)

        ws.write(0, 0, 'Periodo', style1)
        ws.write(0, 1, 'Importe del Capital Social o Participaciones Sociales al cierre del ejercicio o periodo que corresponda', style1)
        ws.write(0, 2, 'Valor nominal por acción o participación social', style1)
        ws.write(0, 3, 'Número de acciones o participaciones sociales suscritas', style1)
        ws.write(0, 4, 'Número de acciones o participaciones sociales pagadas', style1)
        ws.write(0, 5, 'Indica el estado de la operación', style1)

        date = self.obj.date_end.strftime('%Y%m%d')
        i = 1

        values = []

        for k in self.data.keys():
            if self.data[k]:

                for line_data in self.data[k]:

                    balance = abs(line_data.get('balance', 0.00))

                    ws.write(i, 0, date)
                    ws.write(i, 1, balance, style_number)
                    ws.write(i, 2, '1')
                    ws.write(i, 3, balance, style_number)
                    ws.write(i, 4, balance, style_number)
                    ws.write(i, 5, '1')
                    i += 1
                    values.append({'balance': balance})

        workbook.close()
        output.seek(0)

        self.obj.line_ids_316_01.unlink()
        self.obj.line_ids_316_01 = self.obj.env['ple.report.inv.bal.line.16.1'].create(values).ids
        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Capital_{}.xlsx'.format(year_month)


class ReportInvBalSixteenTxt(object):

    def __init__(self, obj, data_1):
        self.obj = obj
        self.data_1 = data_1
        self.ind = 0

    def get_content(self):
        raw = ''
        template = '{period}|{social_capital}|1|{actions_number}|{payed_actions_number}|1|\r\n'
        period = self.obj.date_end.strftime('%Y%m%d')

        self.ind = 0

        for value in self.obj.line_ids_316_01:
            balance = '{:.2f}'.format(abs(value.balance))
            raw += template.format(
                period=period,
                social_capital=balance,
                actions_number=balance,
                payed_actions_number=balance,
            )
            self.ind = 1
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}031601{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(self.ind)
        )
