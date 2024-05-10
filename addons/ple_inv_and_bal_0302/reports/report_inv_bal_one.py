from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportInvBalOneExcel(object):

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

        ws = workbook.add_worksheet('Report Cash')
        ws.set_column('A:H', 15)

        ws.set_row(0, 50)

        ws.write(0, 0, 'Periodo', style1)
        ws.write(0, 1, 'Código de la Cuenta', style1)
        ws.write(0, 2, 'Denominación', style1)
        ws.write(0, 3, 'Codigo de la Entidad Financiera', style1)
        ws.write(0, 4, 'Número de la cuenta de la Entidad Financiera', style1)
        ws.write(0, 5, 'Tipo de moneda', style1)
        ws.write(0, 6, 'Saldo deudor de la cuenta', style1)
        ws.write(0, 7, 'Saldo acreedor de la cuenta', style1)
        ws.write(0, 8, 'Indica el estado de la operación', style1)

        i = 1
        for value in self.data:
            ws.write(i, 0, value['period'])
            ws.write(i, 1, value['accounting_account'])
            ws.write(i, 2, value['bank_account_name'])
            ws.write(i, 3, value['bic'])
            ws.write(i, 4, value['account_bank_code'])
            ws.write(i, 5, value['type_currency'])
            ws.write(i, 6, value['debit_balance'], style_number)
            ws.write(i, 7, value['credit_balance'], style_number)
            ws.write(i, 8, value['status'])
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Efectivo y Equivalente de efectivo_{}.xlsx'.format(year_month)


class ReportInvBalOneTxt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        raw = ''
        template = '{period}|{accounting_account}|{bic}|{account_bank_code}|{type_currency}|{debit_balance}|{credit_balance}|{status}|\r\n'

        for value in self.data:
            raw += template.format(
                period=value['period'],
                accounting_account=value['accounting_account'],
                bic=value['bic'],
                account_bank_code=value['account_bank_code'],
                type_currency=value['type_currency'],
                credit_balance="{:.2f}".format(float(value['credit_balance'] or 0.0)),
                debit_balance="{:.2f}".format(float(value['debit_balance'] or 0.0)),
                status=value['status']
            )
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}030200{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data))
        )
