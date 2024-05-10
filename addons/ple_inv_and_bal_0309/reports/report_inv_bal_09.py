from io import BytesIO
import re

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportInvBalNineExcel(object):

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
            'num_format': '#,##0.00',
        })
        style_date = workbook.add_format({
            'size': 11,
            'num_format': 'dd/mm/yyyy',
        })

        ws = workbook.add_worksheet('Report CXC Empresa')
        ws.set_column('A:H', 15)

        ws.set_row(0, 50)

        ws.write(0, 0, 'Periodo', style1)
        ws.write(0, 1, 'CUO', style1)
        ws.write(0, 2, 'Numero Correlativo', style1)
        ws.write(0, 3, 'Fecha de inicio de la operación', style1)
        ws.write(0, 4, 'Código de la cuenta contable', style1)
        ws.write(0, 5, 'Descripción del intangible', style1)
        ws.write(0, 6, 'Valor contable del intangible', style1)
        ws.write(0, 7, 'Amortización contable acumulada', style1)
        ws.write(0, 8, 'Estado de la operación', style1)

        data = []

        for i in range(len(self.data_1)):
            join = {**self.data_1[i]}
            data.append(join)
        i = 1
        for value in data:
            ws.write(i, 0, value['date'])
            ws.write(i, 1, re.sub(r"[^a-zA-Z0-9]", "", value['name_s']))
            ws.write(i, 2, value['ple_correlative'])
            ws.write(i, 3, value['operation_date'], style_date)
            ws.write(i, 4, re.sub(r'[^a-zA-Z0-9]', '', value['code_account']))
            ws.write(i, 5, value['name_aml'])
            ws.write(i, 6, value['balance'])
            ws.write(i, 7, value['balance_amortization_xls'])
            ws.write(i, 8, value['state'])
            ws.write(i, 9, '|')
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Activos_Intangibles_{}.xlsx'.format(year_month)


class ReportInvBalNineTxt(object):

    def __init__(self, obj, data_1):
        self.obj = obj
        self.data_1 = data_1

    def get_content(self):
        raw = ''
        template = '{date}|{name}|{correlative}|{operation}|{code_account}|{name_aml}|{balance}|{amount_balance}|{state}|\r\n'

        data = []
        for i in range(len(self.data_1)):
            join = {**self.data_1[i]}
            data.append(join)
        for value in data:
            raw += template.format(
                date=value['date'] if value['date'] else '',
                name=re.sub(r"[^a-zA-Z0-9]", "", value['name_s']) if value['name_s'] else '',
                correlative=value['ple_correlative'] if value['ple_correlative'] else '',
                operation=value['operation_date'].strftime("%d/%m/%Y") if value['operation_date'] else '',
                code_account= re.sub(r'[^a-zA-Z0-9]', '', value['code_account']) if value['code_account'] else '',
                name_aml=value['name_aml'] if value['name_aml'] else '',
                balance="%s.00" % int(value['balance']) if value['balance'] else "0.00",
                amount_balance="%s.00" % int(value['balance_amortization_xls']) if value['balance_amortization_xls'] else "0.00",
                state=value['state'],
            )

        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}030900{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data_1))
        )
