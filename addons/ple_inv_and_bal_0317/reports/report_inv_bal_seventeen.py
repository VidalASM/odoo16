from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportInvBalExcel(object):

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

        ws = workbook.add_worksheet('Inver Mob')
        ws.set_column('A:E', 10)

        ws.set_row(0, 50)

        ws.write(0, 0, 'Periodo', style1)
        ws.write(0, 1,
                 'Código de la cuenta contable utilizado en el Balance de Comprobación que se presenta en la declaración pago anual del impuesto a la renta tercera categoría',
                 style1)
        ws.write(0, 2, 'Saldos iniciales Debe', style1)
        ws.write(0, 3, 'Saldos iniciales Haber', style1)
        ws.write(0, 4, 'Movimientos del ejercicio o periodo - Debe', style1)
        ws.write(0, 5, 'Movimientos del ejercicio o periodo - Haber', style1)
        ws.write(0, 6, 'Sumas del Mayor - Debe', style1)
        ws.write(0, 7, 'Sumas del Mayor - haber', style1)
        ws.write(0, 8, 'Saldos al 31 de Diciembre - Deudor', style1)
        ws.write(0, 9, 'Saldos al 31 de Diciembre - Acreedor', style1)
        ws.write(0, 10, 'Transferencias y Cancelaciones - Debe', style1)
        ws.write(0, 11, 'Transferencias y Cancelaciones - Haber', style1)
        ws.write(0, 12, 'Cuentas de Balance - Activo', style1)
        ws.write(0, 13, 'Cuentas de Balance - Pasivo', style1)
        ws.write(0, 14, 'Resultado por Naturaleza - Pérdidas', style1)
        ws.write(0, 15, 'Resultado por Naturaleza - Ganancias', style1)
        ws.write(0, 16, 'Adiciones', style1)
        ws.write(0, 17, 'Deducciones', style1)
        ws.write(0, 18, 'Estado', style1)

        i = 1
        for value in self.data:
            ws.write(i, 0, value['period'])
            ws.write(i, 1, value['code'])
            ws.write(i, 2, value['initial_debit'], style_number)
            ws.write(i, 3, value['initial_credit'], style_number)
            ws.write(i, 4, value['movement_debit'], style_number)
            ws.write(i, 5, value['movement_credit'], style_number)
            ws.write(i, 6, value['higher_sum_debit'], style_number)
            ws.write(i, 7, value['higher_sum_credit'], style_number)
            ws.write(i, 8, value['balance_of_december_debtor'], style_number)
            ws.write(i, 9, value['balance_of_december_creditor'], style_number)
            ws.write(i, 10, value['transfer_cancellation_debit'], style_number)
            ws.write(i, 11, value['transfer_cancellation_credit'], style_number)
            ws.write(i, 12, value['active_balance_account'], style_number)
            ws.write(i, 13, value['passive_balance_account'], style_number)
            ws.write(i, 14, value['result_losses'], style_number)
            ws.write(i, 15, value['result_earnings'], style_number)
            ws.write(i, 16, value['addition'], style_number)
            ws.write(i, 17, value['deduction'], style_number)
            ws.write(i, 18, value['state'])
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Balance_Comprobación_{}.xlsx'.format(year_month)


class ReportInvBalTxt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        raw = ''
        template = '{period}|{code}|{initial_debit}|{initial_credit}|{movement_debit}|{movement_credit}|' \
                   '{higher_sum_debit}|{higher_sum_credit}|{balance_of_december_debtor}|{balance_of_december_creditor}' \
                   '|{transfer_cancellation_debit}|{transfer_cancellation_credit}|{active_balance_account}|' \
                   '{passive_balance_account}|{result_losses}|{result_earnings}|{addition}|{deduction}|{state}|\r\n'

        for value in self.data:
            raw += template.format(
                period=value['period'],
                code=value['code'],
                initial_debit="{:.2f}".format(value['initial_debit']),
                initial_credit="{:.2f}".format(value['initial_credit']),
                movement_debit="{:.2f}".format(value['movement_debit']),
                movement_credit="{:.2f}".format(value['movement_credit']),
                higher_sum_debit="{:.2f}".format(value['higher_sum_debit']),
                higher_sum_credit="{:.2f}".format(value['higher_sum_credit']),
                balance_of_december_debtor="{:.2f}".format(value['balance_of_december_debtor']),
                balance_of_december_creditor="{:.2f}".format(value['balance_of_december_creditor']),
                transfer_cancellation_debit="{:.2f}".format(value['transfer_cancellation_debit']),
                transfer_cancellation_credit="{:.2f}".format(value['transfer_cancellation_credit']),
                active_balance_account="{:.2f}".format(value['active_balance_account']),
                passive_balance_account="{:.2f}".format(value['passive_balance_account']),
                result_losses="{:.2f}".format(value['result_losses']),
                result_earnings="{:.2f}".format(value['result_earnings']),
                addition="{:.2f}".format(value['addition']),
                deduction="{:.2f}".format(value['deduction']),
                state=value['state'],
            )
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}031700{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data))
        )
