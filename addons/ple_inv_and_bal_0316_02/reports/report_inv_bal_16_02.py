from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportInvBalSixteen02Excel(object):

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
        ws.write(0, 1, 'Tipo de Documento de Identidad del accionista o socio', style1)
        ws.write(0, 2, 'Número de Documento de Identidad del accionista o socio', style1)
        ws.write(0, 3, 'Código de los tipos de acciones o participaciones', style1)
        ws.write(0, 4, 'Apellidos y Nombres, Denominación o Razón Social del accionista o socio, según corresponda', style1)
        ws.write(0, 5, 'Número de acciones o de participaciones sociales', style1)
        ws.write(0, 6, 'Porcentaje Total de participación de acciones o participaciones sociales', style1)
        ws.write(0, 7, 'Indica el estado de la operación', style1)

        date = self.obj.date_end.strftime('%Y%m%d')
        i = 1

        for line in self.data:
            if '.' in str(round(line.participations_percentage, 2)):
                x = str(round(line.participations_percentage, 2)).split('.')
                if len(x[1]) < 2:
                    deci = x[0] + '.' + x[1].rjust(2, '0')
                else:
                    deci = x[0] + '.' + x[1]
            else:
                deci = '0.00'

            ws.write(i, 0, date)
            ws.write(i, 1, line.document_type.l10n_pe_vat_code)
            ws.write(i, 2, line.identification_number)
            ws.write(i, 3, line.partition_type_code)
            ws.write(i, 4, line.social_reason.name)
            ws.write(i, 5, str(line.participations_number).replace(',', ''), style_number)
            ws.write(i, 6, deci, style_number)
            ws.write(i, 7, '1')
            i += 1

        workbook.close()
        output.seek(0)

        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Estructura_Accionaria_Participaciones_Sociales_{}.xlsx'.format(year_month)


class ReportInvBalSixteen02Txt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data
        self.ind = 0

    def get_content(self):
        raw = ''
        template = '{period}|{vat_code}|{vat}|{partition_type_code}|{partner_name}|{participations_number}|{participations_percentage}|1|\n'
        period = self.obj.date_end.strftime('%Y%m%d')

        self.ind = 0

        for value in self.data:
            if '.' in str(round(value.participations_percentage, 2)):
                x = str(round(value.participations_percentage, 2)).split('.')
                if len(x[1]) < 2:
                    deci = x[0] + '.' + x[1].rjust(2, '0')
                else:
                    deci = x[0] + '.' + x[1]
            else:
                deci = '0.00'

            raw += template.format(
                period=period,
                vat_code=value.document_type.l10n_pe_vat_code,
                vat=value.identification_number,
                partition_type_code=value.partition_type_code,
                partner_name=value.social_reason.name,
                participations_number=(str(value.participations_number)).replace(',', ''),
                participations_percentage=deci
            )
            self.ind = 1
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}031602{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send,
            has_info=self.ind
        )
