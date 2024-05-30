from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class AssetsReport03(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content_excel(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        style_column = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'size': 10,
            'bold': True,
            'border': 7
        })
        style_content = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'border': 7
        })
        style_number = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
            'border': 7
        })
        style_date = workbook.add_format({
            'size': 10,
            'num_format': 'dd/mm/yy',
            'border': 7
        })

        ws = workbook.add_worksheet('REGISTRO DE ACTIVOS FIJOS - REVALUADOS Y NO REVALUADOS')
        ws.set_column('A:A', 15)
        ws.set_column('B:B', 40)
        ws.set_column('C:C', 40)
        ws.set_column('D:D', 40)
        ws.set_column('E:E', 40)
        ws.set_column('F:F', 40)
        ws.set_column('G:G', 40)
        ws.set_column('H:H', 40)
        ws.set_column('I:I', 40)
        ws.set_column('J:J', 40)
        ws.set_column('K:K', 40)
        ws.set_column('L:L', 40)
        ws.set_column('M:M', 40)
        ws.set_column('N:U', 20)
        ws.set_column('V:AI', 25)

        ws.set_row(0, 50)

        ws.write(0, 0, 'Periodo', style_column)
        ws.write(0, 1, 'CUO', style_column)
        ws.write(0, 2, 'Número correlativo del asiento', style_column)
        ws.write(0, 3, 'Código del catálogo utilizado', style_column)
        ws.write(0, 4, 'Número del contrato de arrendamiento financiero del Activo Fijo', style_column)
        ws.write(0, 5, 'Fecha del contrato de arrendamiento financiero del Activo Fijo', style_column)
        ws.write(0, 6, 'Código propio del activo fijo', style_column)
        ws.write(0, 7, 'Fecha de inicio del arrendamiento financiero del Activo Fijo', style_column)
        ws.write(0, 8, 'Número de cuotas pactadas', style_column)
        ws.write(0, 9, 'Monto total del contrato de arrendamiento financiero del Activo Fijo', style_column)
        ws.write(0, 10, 'Indica el estado de la operación', style_column)

        i = 1
        period = self.obj.date_end.strftime('%Y%m%d')
        for value in self.data:
            ws.write(i, 0, period, style_content)
            ws.write(i, 1, value['cuo'], style_content)
            ws.write(i, 2, value['ple_correlative'], style_content)
            ws.write(i, 3, value['asset_catalog_code'], style_content)
            ws.write(i, 4, value['contract_number'], style_content)
            ws.write(i, 5, value['acquisition_date'], style_date)
            ws.write(i, 6, value['asset_code'], style_content)
            ws.write(i, 7, value['asset_date_init'], style_date)
            ws.write(i, 8, value['method_number'], style_content)
            ws.write(i, 9, value['original_value'], style_number)
            ws.write(i, 10, 1, style_content)

            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self, file_type, book_identifier):
        year = self.obj.date_start.strftime('%Y')
        return 'LE{vat}{period_year}{period_month}{period_day}{book_identifier}00{state_send}{has_info}11.{file_type}'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month='00',
            period_day='00',
            book_identifier=book_identifier,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data)),
            file_type=file_type
        )

    def get_content_txt(self):
        raw = ''
        template = '{period}|{cuo}|{ple_correlative}|{asset_catalog_code}|{contract_number}|{acquisition_date}|' \
                   '{asset_code}|{asset_date_init}|{method_number}|{original_value}|1|\r\n'

        period = self.obj.date_start.strftime('%Y0000')
        for value in self.data:
            raw += template.format(
                period=period,
                cuo=value['cuo'],
                ple_correlative=value['ple_correlative'],
                asset_catalog_code=value['asset_catalog_code'],
                contract_number=value['contract_number'],
                acquisition_date=value['acquisition_date'],
                asset_code=value['asset_code'],
                asset_date_init=value['asset_date_init'],
                method_number=value['method_number'],
                original_value="{0:.2f}".format(value['original_value']),
            )
        return raw
