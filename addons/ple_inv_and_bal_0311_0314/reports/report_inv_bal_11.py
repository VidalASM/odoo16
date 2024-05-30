from io import BytesIO
import re

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportInvBal11Excel(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_filename(self):
        return f"Libro_Remuner_Particip_por_pagar_{self.obj.date_end.strftime('%Y%m')}.xlsx"

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = workbook.add_worksheet('Report de Venta')

        style0 = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
            'border': 7
        })
        style1 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
            'border': 7
        })
        style2 = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'font_name': 'Arial',
            'bold': True
        })
        style3 = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'font_name': 'Arial'
        })
        content_number_format_bold = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
            'bold': True
        })
        content_number_format = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
        })
        content_date_format = workbook.add_format({
            'align': 'right',
            'size': 10,
            'num_format': 'dd/mm/yy',
        })

        i = 0

        ws.set_column('A:A', 12)
        ws.set_column('B:B', 14)
        ws.set_column('C:C', 18)
        ws.set_column('D:D', 10)
        ws.set_column('E:E', 22)
        ws.set_column('F:F', 17)
        ws.set_column('G:G', 30)
        ws.set_column('H:H', 30)
        ws.set_column('I:I', 17)
        ws.set_row(0, 50)

        ws.write(i, 0, 'Periodo', style1)
        ws.write(i, 1, 'CUO', style1)
        ws.write(i, 2, 'Número Correlativo', style1)
        ws.write(i, 3, 'Cuenta', style1)
        ws.write(i, 4, 'Tipo de Identificación', style1)
        ws.write(i, 5, 'Nro. de doc.', style1)
        ws.write(i, 6, 'Código del trabajador', style1)
        ws.write(i, 7, 'Apellidos y Nombres del trabajador', style1)
        ws.write(i, 8, 'Saldo Final', style1)
        i += 1

        period = self.obj.date_end.strftime('%Y%m%d')

        values = []

        for k in self.data.keys():
            if self.data[k]:

                for line_data in self.data[k]:
                    ws.write(i, 0, period, style3)
                    ws.write(i, 1, line_data.get('move', ''), style3)
                    ws.write(i, 2, line_data.get('ple_correlative', ''), style3)
                    ws.write(i, 3, re.sub(r'[^a-zA-Z0-9]', '',line_data.get('account', '')), style3)
                    ws.write(i, 4, line_data.get('l10n_latam_identification_type_id', ''), style3)
                    ws.write(i, 5, line_data.get('vat', ''), style3)
                    ws.write(i, 6, line_data.get('vat', ''), style3)
                    ws.write(i, 7, line_data.get('partner', ''), style3)
                    ws.write(i, 8, line_data.get('balance', 0.00), content_number_format)
                    i += 1

                    values.append({'move': line_data.get('move', ''),
                                   'ple_correlative': line_data.get('ple_correlative', ''),
                                   'account':  re.sub(r'[^a-zA-Z0-9]', '', line_data.get('account', '')),
                                   'l10n_latam_identification_type_id': line_data.get('l10n_latam_identification_type_id', ''),
                                   'vat': line_data.get('vat', ''),
                                   'partner': line_data.get('partner', ''),
                                   'balance': line_data.get('balance', 0.00),
                                   'name': line_data.get('name', ''),
                                   })

        workbook.close()
        output.seek(0)

        self.obj.line_ids_311 = self.obj.env['ple.report.inv.bal.line.11'].create(values).ids
        return output.read()


class ReportInvBal11Txt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data
        self.ind = 0

    def get_content(self):
        raw = ''
        template = '{period}|{move}|{ple_correlative}|{account}|{l10n_latam_identification_type_id}|{vat}|{vat}|{partner}|{balance}|1|\r\n'
        period = self.obj.date_end.strftime('%Y%m%d')

        self.ind = 0

        for value in self.obj.line_ids_311:
            raw += template.format(
                period=period,
                move=value.move,
                ple_correlative=value.ple_correlative,
                account= re.sub(r'[^a-zA-Z0-9]', '', value.account),
                l10n_latam_identification_type_id=value.l10n_latam_identification_type_id,
                vat=value.vat,
                partner=value.partner,
                balance='{:.2f}'.format(value.balance),
            )
            self.ind = 1

        return raw

    def get_filename(self):
        return 'LE{vat}{period}031100{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period=self.obj.date_end.strftime('%Y%m%d'),
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=self.ind,
        )