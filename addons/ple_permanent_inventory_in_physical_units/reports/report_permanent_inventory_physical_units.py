from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class PermanentInventoryPhysicalUnitsReport(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content_excel(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        style_column = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
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

        ws = workbook.add_worksheet('12 Estructura del Registro de Inventario Permanente en Unidades físicas')
        ws.set_column('A:A', 15)
        ws.set_column('B:R', 40)
        ws.set_row(0, 50)

        ws.write(0, 0, 'Fila', style_column)
        ws.write(0, 1, 'Periodo', style_column)
        ws.write(0, 2, 'CUO', style_column)
        ws.write(0, 3, 'Número correlativo del asiento', style_column)
        ws.write(0, 4, 'Establecimiento', style_column)
        ws.write(0, 5, 'Catálogo de existencias', style_column)
        ws.write(0, 6, 'Tipo de existencia', style_column)
        ws.write(0, 7, 'Código del producto', style_column)
        ws.write(0, 8, 'Código del Catálogo', style_column)
        ws.write(0, 9, 'Código de la existencia', style_column)
        ws.write(0, 10, 'Fecha de inicio', style_column)
        ws.write(0, 11, 'Tipo de comprobante de pago', style_column)
        ws.write(0, 12, 'Serie de comprobante de pago', style_column)
        ws.write(0, 13, 'Número de comprobante de pago', style_column)
        ws.write(0, 14, 'Tipo de operación efectuada', style_column)
        ws.write(0, 15, 'Descripción del producto', style_column)
        ws.write(0, 16, 'Código UDM', style_column)
        ws.write(0, 17, 'Cantidad de unidades físicas del bien ingresado', style_column)
        ws.write(0, 18, 'Cantidad de unidades físicas del bien retirado', style_column)
        ws.write(0, 19, 'Estado de la operación', style_column)

        i = 1
        for value in self.data:
            if value['header']:
                ws.merge_range(i, 0, i, 17, value['stock_description'].upper(), style_content)
                i += 1
            ws.write(i, 0, i, style_content)
            ws.write(i, 1, value['period'], style_content)
            ws.write(i, 2, value['cuo'], style_content)
            ws.write(i, 3, value['correlative'], style_content)
            ws.write(i, 4, value['annexed_establishment_code'], style_content)
            ws.write(i, 5, value['stock_catalog'], style_content)
            ws.write(i, 6, value['stock_type'], style_content)
            ws.write(i, 7, value['stock_own_code'], style_content)
            ws.write(i, 8, value['catalog_code'], style_content)
            ws.write(i, 9, value['stock_code'], style_content)
            ws.write(i, 10, value['valuation_date'], style_content)
            ws.write(i, 11, value['document_type'], style_content)
            ws.write(i, 12, value['series'], style_content)
            ws.write(i, 13, value['document_number'], style_content)
            ws.write(i, 14, value['operation_type'], style_date)
            ws.write(i, 15, value['description'], style_content)
            ws.write(i, 16, value['unit_measure_code'], style_content)
            ws.write(i, 17, value['qty_physical_units_asset_entered'], style_number)
            ws.write(i, 18, value['qty_physical_units_asset_removed'], style_number)
            ws.write(i, 19, value['state'], style_content)
            ws.write(i, 20, '', style_content)
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_content_txt(self):
        raw = ''
        template = '{period}|{cuo}|{correlative}|{annexed_establishment_code}|{stock_catalog}|' \
                   '{stock_type}|{stock_own_code}|{catalog_code}|{stock_code}|{valuation_date}|{document_type}|' \
                   '{series}|{document_number}|{operation_type}|{description}|{unit_measure_code}|' \
                   '{qty_physical_units_asset_entered}|{qty_physical_units_asset_removed}|{state}|\r\n'

        for value in self.data:
            raw += template.format(
                period=value['period'],
                cuo=value['cuo'],
                correlative=value['correlative'],
                annexed_establishment_code=value['annexed_establishment_code'],
                stock_catalog=value['stock_catalog'],

                stock_type=value['stock_type'],
                stock_own_code=value['stock_own_code'],
                catalog_code=value['catalog_code'],
                stock_code=value['stock_code'],
                valuation_date=value['valuation_date'],
                document_type=value['document_type'],

                series=value['series'],
                document_number=value['document_number'],
                operation_type=value['operation_type'],
                description=value['description'],
                unit_measure_code=value['unit_measure_code'],

                qty_physical_units_asset_entered="{0:.2f}".format(value['qty_physical_units_asset_entered']),
                qty_physical_units_asset_removed="{0:.2f}".format(value['qty_physical_units_asset_removed']),
                state=value['state'],
            )
        return raw

    def get_filename(self, file_type):
        year = self.obj.date_start.strftime('%Y')
        month = self.obj.date_start.strftime('%m')
        return 'LE{vat}{period_year}{period_month}00{book_identifier}00{state_send}{has_info}11.{file_type}'.format(
            vat=self.obj.company_id.vat or '00000000000',
            period_year=year,
            period_month=month,
            book_identifier='120100',
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data)),
            file_type=file_type
        )

    def get_file_excel(self, file_type):
        year = self.obj.date_start.strftime('%Y')
        month = self.obj.date_start.strftime('%m')

        return 'Libro de Unidades_{vat}_{period_year}{period_month}.{file_type}'.format(
            vat=self.obj.company_id.name,
            period_year=year,
            period_month=month,
            file_type=file_type
        )
