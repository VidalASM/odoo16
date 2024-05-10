from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class LedgerReportExcel(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
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

        ws = workbook.add_worksheet('Report valuation')
        ws.set_column('A:A', 5)
        ws.set_column('B:B', 15)
        ws.set_column('C:C', 30)
        ws.set_column('D:D', 20)
        ws.set_column('E:E', 15)
        ws.set_column('F:F', 20)
        ws.set_column('G:G', 20)
        ws.set_column('H:H', 20)
        ws.set_column('I:I', 15)
        ws.set_column('J:J', 15)
        ws.set_column('K:K', 20)
        ws.set_column('L:L', 15)
        ws.set_column('M:M', 15)
        ws.set_column('N:N', 15)
        ws.set_column('O:O', 15)
        ws.set_column('P:P', 30)
        ws.set_column('Q:Q', 15)
        ws.set_column('R:R', 15)
        ws.set_column('S:S', 15)
        ws.set_column('T:T', 15)
        ws.set_column('U:U', 15)
        ws.set_column('V:V', 15)
        ws.set_column('W:W', 15)
        ws.set_column('X:X', 15)
        ws.set_column('Y:Y', 15)
        ws.set_column('Z:Z', 15)
        ws.set_column('AA:AA', 15)

        ws.set_row(0, 50)

        ws.write(0, 0, 'Fila', style_column)
        ws.write(0, 1, 'Periodo', style_column)
        ws.write(0, 2, 'CUO', style_column)
        ws.write(0, 3, 'Número correlativo del asiento', style_column)
        ws.write(0, 4, 'Establecimiento', style_column)
        ws.write(0, 5, 'Catálogo de existencia', style_column)
        ws.write(0, 6, 'Tipo de existencia', style_column)
        ws.write(0, 7, 'Código del producto', style_column)
        ws.write(0, 8, 'Catalogo de existencia UNSPSC', style_column)
        ws.write(0, 9, 'Código UNSPSC', style_column)
        ws.write(0, 10, 'Fecha de inicio', style_column)
        ws.write(0, 11, 'Tipo de comprobante de pago', style_column)
        ws.write(0, 12, 'Serie de comprobante de pago', style_column)
        ws.write(0, 13, 'Número de comprobante de pago', style_column)
        ws.write(0, 14, 'Tipo de operación', style_column)
        ws.write(0, 15, 'Descripción del producto', style_column)
        ws.write(0, 16, 'Código UDM', style_column)
        ws.write(0, 17, 'código del metodo de evalucion de existencia', style_column)
        ws.write(0, 18, 'Cantidad de unidades físcas del bien ingresado', style_column)
        ws.write(0, 19, 'Costo unitario del bien ingresado', style_column)
        ws.write(0, 20, 'Costo total del bien ingresado', style_column)
        ws.write(0, 21, 'Cantidad de unidades físicas del bien retirado', style_column)
        ws.write(0, 22, 'Costo unitario del bien retirado', style_column)
        ws.write(0, 23, 'Costo total del bien retirado', style_column)
        ws.write(0, 24, 'Cantidad de unidades físicas del saldo final', style_column)
        ws.write(0, 25, 'Costo unitario del saldo final', style_column)
        ws.write(0, 26, 'Costo total  del saldo final', style_column)
        ws.write(0, 27, 'Estado de la operación', style_column)

        i = 1
        for value in self.data:
            if value['header']:
                ws.merge_range(i, 0, i, 27, value['description_prod'], style_content)
                i += 1

            ws.write(i, 0, i, style_content)
            ws.write(i, 1, value['period'], style_content)
            ws.write(i, 2, value['cou'], style_content)
            ws.write(i, 3, value['correlativo'], style_content)
            ws.write(i, 4, value['establishment'], style_content)
            ws.write(i, 5, value['catalog'], style_content)
            ws.write(i, 6, value['stock_type'], style_content)
            ws.write(i, 7, value['default_code'], style_content)
            ws.write(i, 8, value['code_catag'], style_content)
            ws.write(i, 9, value['unspsc_code'], style_content)
            ws.write(i, 10, value['date_start'], style_content)
            ws.write(i, 11, value['number_document'], style_content)
            ws.write(i, 12, value['serie_document'], style_content)
            ws.write(i, 13, value['reference_document'], style_content)
            ws.write(i, 14, value['type_operation'], style_content)
            ws.write(i, 15, value['description'], style_content)
            ws.write(i, 16, value['uom'], style_content)
            ws.write(i, 17, value['code_exist'], style_content)
            ws.write(i, 18, value['quantity_product_hand'], style_number)
            ws.write(i, 19, value['standard_price'], style_number)
            ws.write(i, 20, value['total_value'], style_number)
            ws.write(i, 21, value['quantity'], style_number)
            ws.write(i, 22, value['unit_cost'], style_number)
            ws.write(i, 23, value['value_cost'], style_number)
            ws.write(i, 24, value['quantity_hand_accumulated'], style_number)
            ws.write(i, 25, value['cost_unit_accumulated'], style_number)
            ws.write(i, 26, value['cost_total_accumulated'], style_number)
            ws.write(i, 27, value['state'], style_content)
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        name = self.obj.date_start.strftime('%Y%m')
        return 'Libro valorizado_{}_{}.xlsx'.format(self.obj.company_id.name, name)


class LedgerReportTxt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        raw = ''
        template = '{period}|{cou}|{correlativo}|' \
                   '{establishment}|{catalog}|{stock_type}|' \
                   '{default_code}|{code_catag}|' \
                   '{unspsc_code}|{date_start}|{number_document}|' \
                   '{serie_document}|{reference_document}|{type_operation}|' \
                   '{description}|{uom}|{code_exist}|' \
                   '{quantity_product_hand}|{standard_price}|{total_value}|' \
                   '{quantity}|{unit_cost}|{value_cost}|' \
                   '{quantity_hand_accumulated}|{cost_unit_accumulated}|{cost_total_accumulated}|' \
                   '{state}|\r\n'
        for value in self.data:
            raw += template.format(
                period=value['period'],
                cou=value['cou'],
                correlativo=value['correlativo'],
                establishment=value['establishment'],
                catalog=value['catalog'],
                stock_type=value['stock_type'],
                default_code=value['default_code'],
                code_catag=value['code_catag'],
                unspsc_code=value['unspsc_code'],
                date_start=value['date_start'],
                number_document=value['number_document'],
                serie_document=value['serie_document'],
                reference_document=value['reference_document'],
                type_operation=value['type_operation'],
                description=value['description'],
                uom=value['uom'],
                code_exist=value['code_exist'],
                quantity_product_hand="{0:.2f}".format(value['quantity_product_hand']),
                standard_price="{0:.2f}".format(value['standard_price']),
                total_value="{0:.2f}".format(value['total_value']),
                quantity="{0:.2f}".format(value['quantity']),
                unit_cost="{0:.2f}".format(value['unit_cost']),
                value_cost="{0:.2f}".format(value['value_cost']),
                quantity_hand_accumulated="{0:.2f}".format(value['quantity_hand_accumulated']),
                cost_unit_accumulated="{0:.2f}".format(value['cost_unit_accumulated']),
                cost_total_accumulated="{0:.2f}".format(value['cost_total_accumulated']),
                state=value['state'],
            )
        return raw

    def get_filename(self, type='01'):
        year, month = self.obj.date_start.strftime('%Y/%m').split('/')
        return 'LE{vat}{period_year}{period_month}0013010000{state_send}{has_info}{currency}1.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            state_send=self.obj.state_send or '',
            currency='1',
            has_info=int(bool(self.data))
        )
