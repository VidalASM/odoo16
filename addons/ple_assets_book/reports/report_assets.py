from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class AssetsReport(object):

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
        ws.write(0, 4, 'Código propio del activo fijo', style_column)
        ws.write(0, 5, 'Código de catalogo utilizado', style_column)
        ws.write(0, 6, 'Código de la existencia', style_column)
        ws.write(0, 7, 'Código del tipo de Activo Fijo', style_column)
        ws.write(0, 8, 'Código de la Cuenta Contable del Activo Fijo', style_column)
        ws.write(0, 9, 'Estado del Activo Fijo', style_column)
        ws.write(0, 10, 'Descripción del Activo Fijo', style_column)

        ws.write(0, 11, 'Marca del Activo Fijo', style_column)
        ws.write(0, 12, 'Modelo del Activo Fijo', style_column)
        ws.write(0, 13, 'Número de serie y/o placa del Activo Fijo', style_column)
        ws.write(0, 14, 'Importe del saldo inicial del Activo Fijo', style_column)
        ws.write(0, 15, 'Importe de las adquisiciones o adiciones de Activo Fijo', style_column)
        ws.write(0, 16, 'Importe de las mejoras del Activo Fijo', style_column)
        ws.write(0, 17, 'Importe de los retiros y/o baºjas del Activo Fijo', style_column)
        ws.write(0, 18, 'Importe por otros ajustes en el valor del Activo Fijo', style_column)
        ws.write(0, 19, 'Valor de la revaluación voluntaria efectuada', style_column)
        ws.write(0, 20, 'Valor de la revaluación efectuada por reorganización de sociedades', style_column)

        ws.write(0, 21, 'Valor de otras revaluaciones efectuada', style_column)
        ws.write(0, 22, 'Importe del valor del ajuste por inflación del Activo Fijo', style_column)
        ws.write(0, 23, 'Fecha de adquisición del Activo Fijo', style_column)
        ws.write(0, 24, 'Fecha de inicio del Uso del Activo Fijo', style_column)
        ws.write(0, 25, 'Código del Método aplicado en el cálculo de la depreciación', style_column)
        ws.write(0, 26, 'Número de documento de autorización para cambiar el método de la depreciación', style_column)
        ws.write(0, 27, 'Porcentaje de la depreciación', style_column)
        ws.write(0, 28, 'Depreciación acumulada al cierre del ejercicio anterior.', style_column)
        ws.write(0, 29, 'Valor de la depreciación del ejercicio sin considerar la revaluación', style_column)
        ws.write(0, 30, 'Valor de la depreciación del ejercicio relacionada con los retiros y/o bajas del Activo Fijo', style_column)

        ws.write(0, 31, 'Valor de la depreciación relacionada con otros ajustes', style_column)
        ws.write(0, 32, 'Valor de la depreciación de la revaluación voluntaria efectuada', style_column)
        ws.write(0, 33, 'Valor de la depreciación de la revaluación efectuada por reorganización de sociedades', style_column)
        ws.write(0, 34, 'Valor de la depreciación de otras revaluaciones efectuadas', style_column)
        ws.write(0, 35, 'Valor del ajuste por inflación de la depreciación', style_column)
        ws.write(0, 36, 'Estado de la operación', style_column)

        i = 1
        for value in self.data:
            ws.write(i, 0, value['period'], style_content)
            ws.write(i, 1, value['cuo'], style_content)
            ws.write(i, 2, value['correlative'], style_content)
            ws.write(i, 3, value['asset_catalog_code'], style_content)
            ws.write(i, 4, value['asset_code'], style_content)

            ws.write(i, 5, value['used_catalog_code'], style_content)

            ws.write(i, 6, value['unique_fixed_asset_type'], style_content)
            ws.write(i, 7, value['fixed_asset_type'], style_content)
            ws.write(i, 8, value['account_code'], style_content)
            ws.write(i, 9, value['fixed_asset_state'], style_content)
            ws.write(i, 10, value['description'], style_content)

            ws.write(i, 11, value['asset_brand'], style_content)
            ws.write(i, 12, value['asset_model'], style_content)
            ws.write(i, 13, value['asset_series'], style_content)
            ws.write(i, 14, value['asset_opening'], style_number)
            ws.write(i, 15, value['asset_amount'], style_number)

            ws.write(i, 16, value['amount_improvement'], style_number)
            ws.write(i, 17, value['amount_withdrawals'], style_number)
            ws.write(i, 18, value['amount_other_adjustments'], style_number)
            ws.write(i, 19, value['amount_voluntary_revaluation'], style_number)
            ws.write(i, 20, value['amount_revaluation_reorganization'], style_number)

            ws.write(i, 21, value['amount_other_revaluation'], style_number)
            ws.write(i, 22, value['amount_inflation_adjustment'], style_number)
            ws.write(i, 23, value['acquisition_date'], style_date)
            ws.write(i, 24, value['start_date'], style_date)
            ws.write(i, 25, value['code_calculation_depreciation'], style_content)

            ws.write(i, 26, value['authorization_document_number'], style_content)
            ws.write(i, 27, value['depreciation_percentage'], style_number)
            ws.write(i, 28, value['accumulated_depreciation_end_previous_year'], style_number)
            ws.write(i, 29, value['amount_depreciation_without_revaluation'], style_number)
            ws.write(i, 30, value['amount_depreciation_withdrawals'], style_number)

            ws.write(i, 31, value['amount_depreciation_other_adjustments'], style_number)
            ws.write(i, 32, value['amount_depreciation_voluntary_revaluation'], style_number)
            ws.write(i, 33, value['amount_depreciation_revaluation_reorganization'], style_number)
            ws.write(i, 34, value['amount_depreciation_revaluations'], style_number)
            ws.write(i, 35, value['amount_depreciation_inflation'], style_number)

            ws.write(i, 36,1, style_content)

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

        def format_txt_decimal(values, percent=False):
            if not percent:
                value_format = "{0:.2f}".format(round(values, 2))
            else:
                value_format = "{0:.2f}".format(values)
            return value_format

        raw = ''
        template = '{period}|{cuo}|{correlative}|{asset_catalog_code}|{asset_code}|{used_catalog_code}|' \
                   '{unique_fixed_asset_type}|{fixed_asset_type}|{account_code}|{fixed_asset_state}|{description}|' \
                   '{asset_brand}|{asset_model}|{asset_series}|{asset_opening}|{asset_amount}|' \
                   '{amount_improvement}|{amount_withdrawals}|{amount_other_adjustments}|{amount_voluntary_revaluation}|{amount_revaluation_reorganization}|' \
                   '{amount_other_revaluation}|{amount_inflation_adjustment}|{acquisition_date}|{start_date}|{code_calculation_depreciation}|' \
                   '{authorization_document_number}|{depreciation_percentage}|{accumulated_depreciation_end_previous_year}|{amount_depreciation_without_revaluation}|{amount_depreciation_withdrawals}|' \
                   '{amount_depreciation_other_adjustments}|{amount_depreciation_voluntary_revaluation}|{amount_depreciation_revaluation_reorganization}|{amount_depreciation_revaluations}|{amount_depreciation_inflation}|' \
                   '{state}|\r\n'

        for value in self.data:
            raw += template.format(
                period=value['period'],
                cuo=value['cuo'],
                correlative=value['correlative'],
                asset_catalog_code=value['asset_catalog_code'],
                asset_code=value['asset_code'],

                used_catalog_code=value['used_catalog_code'],

                unique_fixed_asset_type=value['unique_fixed_asset_type'],
                fixed_asset_type=value['fixed_asset_type'],
                account_code=value['account_code'],
                fixed_asset_state=value['fixed_asset_state'],
                description=value['description'],

                asset_brand=value['asset_brand'],
                asset_model=value['asset_model'],
                asset_series=value['asset_series'],
                asset_opening=value['asset_opening'],
                asset_amount="{:.2f}".format(value['asset_amount']),

                amount_improvement="{:.2f}".format(value['amount_improvement']),
                amount_withdrawals="{:.2f}".format(value['amount_withdrawals']),
                amount_other_adjustments="{:.2f}".format(value['amount_other_adjustments']),
                amount_voluntary_revaluation="{:.2f}".format(value['amount_voluntary_revaluation']),
                amount_revaluation_reorganization="{:.2f}".format(value['amount_revaluation_reorganization']),

                amount_other_revaluation="{:.2f}".format(value['amount_other_revaluation']),
                amount_inflation_adjustment=value['amount_inflation_adjustment'],
                acquisition_date=value['acquisition_date'],
                start_date=value['start_date'],
                code_calculation_depreciation=value['code_calculation_depreciation'],

                authorization_document_number=value['authorization_document_number'],
                depreciation_percentage="{:.2f}".format(value['depreciation_percentage']),
                accumulated_depreciation_end_previous_year="{:.2f}".format(value['accumulated_depreciation_end_previous_year']),
                amount_depreciation_without_revaluation="{:.2f}".format(value['amount_depreciation_without_revaluation']),
                amount_depreciation_withdrawals="{:.2f}".format(value['amount_depreciation_withdrawals']),

                amount_depreciation_other_adjustments="{:.2f}".format(value['amount_depreciation_other_adjustments']),
                amount_depreciation_voluntary_revaluation="{:.2f}".format(value['amount_depreciation_voluntary_revaluation']),
                amount_depreciation_revaluation_reorganization="{:.2f}".format(value['amount_depreciation_revaluation_reorganization']),
                amount_depreciation_revaluations="{:.2f}".format(value['amount_depreciation_revaluations']),
                amount_depreciation_inflation="{:.2f}".format(value['amount_depreciation_inflation']),

                state=1
            )
        return raw
