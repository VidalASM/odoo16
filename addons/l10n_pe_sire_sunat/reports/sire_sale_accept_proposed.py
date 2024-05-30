from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class SireSaleAcceptProposedXlsx:
    def __init__(self, obj, processed_results):
        self.obj = obj
        self.processed_results = processed_results

    def __str__(self):
        return "Reporte RVIE - Cuando acepta la propuesta XLSX - {}, {}{}".format(
            self.obj.company_id.name,
            self.obj.year,
            self.obj.month
        )

    @staticmethod
    def _write_headers_report(workbook, worksheet):
        style_header = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
            'font_name': 'Arial',
            'text_wrap': True
        })
        worksheet.write(0, 0, 'Fila', style_header)
        worksheet.write(0, 1, 'RUC', style_header)
        worksheet.write(0, 2, 'ID', style_header)
        worksheet.write(0, 3, 'Periodo', style_header)
        worksheet.write(0, 4, 'CAR SUNAT', style_header)
        worksheet.write(0, 5, 'Fecha de Emisión', style_header)
        worksheet.write(0, 6, 'Fecha Vcto/Pago', style_header)
        worksheet.write(0, 7, 'Tipo CP/Doc', style_header)
        worksheet.write(0, 8, 'Serie del CDP', style_header)
        worksheet.write(0, 9, 'Nro CP o \nDoc. Nro Inicial \n(Rango)', style_header)
        worksheet.write(0, 10, 'Nro Final (Rango)', style_header)
        worksheet.write(0, 11, 'Tipo Doc Identidad', style_header)
        worksheet.write(0, 12, 'Número de RUC o \nDocumento de \nIdentidad del Cliente', style_header)
        worksheet.write(0, 13, 'Apellidos Nombres/ \nRazón Social', style_header)
        worksheet.write(0, 14, 'Valor Facturado \nExportación', style_header)
        worksheet.write(0, 15, 'BI Gravada', style_header)
        worksheet.write(0, 16, 'Dscto BI', style_header)
        worksheet.write(0, 17, 'IGV/IPM', style_header)
        worksheet.write(0, 18, 'Dscto IGV/IPM', style_header)
        worksheet.write(0, 19, 'Mto Exonerado', style_header)
        worksheet.write(0, 20, 'Mto Inafecto', style_header)
        worksheet.write(0, 21, 'ISC', style_header)
        worksheet.write(0, 22, 'BI Grav IVAP', style_header)
        worksheet.write(0, 23, 'IVAP', style_header)
        worksheet.write(0, 24, 'ICBPER', style_header)
        worksheet.write(0, 25, 'Otros Tributos', style_header)
        worksheet.write(0, 26, 'Total CP', style_header)
        worksheet.write(0, 27, 'Moneda', style_header)
        worksheet.write(0, 28, 'Tipo Cambio', style_header)
        worksheet.write(0, 29, 'Fecha Emisión \nDoc Modificado', style_header)
        worksheet.write(0, 30, 'Tipo CP Modificado', style_header)
        worksheet.write(0, 31, 'Serie CP Modificado', style_header)
        worksheet.write(0, 32, 'Nro CP Modificado', style_header)
        worksheet.write(0, 33, 'ID Proyecto \nOperadores \nAtribución', style_header)
        worksheet.write(0, 34, 'CLU', style_header)
        worksheet.write(0, 35, '', style_header)

    @staticmethod
    def _write_rows_report(workbook, worksheet, processed_results):
        style_number_two_decimal = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
        })
        style_number_three_decimal = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.000',
        })
        style_content = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'size': 10,
        })
        style_date = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'size': 10,
            'num_format': 'dd/mm/yy',
        })
        row = 1
        for dict_result in processed_results:
            worksheet.write(row, 0, row, style_content)
            worksheet.write(row, 1, dict_result['company_vat'], style_content)
            worksheet.write(row, 2, dict_result['company_name'], style_content)
            worksheet.write(row, 3, dict_result['period'], style_content)
            worksheet.write(row, 4, '', style_content)
            worksheet.write(row, 5, dict_result['invoice_date'], style_date)
            worksheet.write(row, 6, '', style_date)
            worksheet.write(row, 7, dict_result['document_type_code'], style_content)
            worksheet.write(row, 8, dict_result['invoice_serie'], style_content)
            worksheet.write(row, 9, dict_result['invoice_correlative'], style_content)
            worksheet.write(row, 10, '', style_content)
            worksheet.write(row, 11, dict_result['partner_identification_code'], style_content)
            worksheet.write(row, 12, dict_result['partner_vat'])
            worksheet.write(row, 13, dict_result['partner_name'])
            worksheet.write(row, 14, dict_result['s_base_exp'], style_number_two_decimal)
            worksheet.write(row, 15, dict_result['s_base_og'], style_number_two_decimal)
            worksheet.write(row, 16, dict_result['s_base_ogd'], style_number_two_decimal)
            worksheet.write(row, 17, dict_result['s_tax_og'], style_number_two_decimal)
            worksheet.write(row, 18, dict_result['s_tax_ogd'], style_number_two_decimal)
            worksheet.write(row, 19, dict_result['s_base_oe'], style_number_two_decimal)
            worksheet.write(row, 20, dict_result['s_base_ou'], style_number_two_decimal)
            worksheet.write(row, 21, dict_result['s_tax_isc'], style_number_two_decimal)
            worksheet.write(row, 22, dict_result['s_tax_icbp'], style_number_two_decimal)
            worksheet.write(row, 23, dict_result['s_base_ivap'], style_number_two_decimal)
            worksheet.write(row, 24, dict_result['s_tax_ivap'], style_number_two_decimal)
            worksheet.write(row, 25, dict_result['s_tax_other'], style_number_two_decimal)
            worksheet.write(row, 26, dict_result['amount_total'], style_number_two_decimal)
            worksheet.write(row, 27, dict_result['currency_name'], style_content)
            worksheet.write(row, 28, dict_result['exchange_rate'], style_number_three_decimal)
            worksheet.write(row, 29, dict_result['origin_invoice_date'], style_date)
            worksheet.write(row, 30, dict_result['origin_document_type_code'], style_content)
            worksheet.write(row, 31, dict_result['origin_number_serie'], style_content)
            worksheet.write(row, 32, dict_result['origin_number_correlative'], style_content)
            worksheet.write(row, 33, '', style_content)
            worksheet.write(row, 34, dict_result['detraction'], style_content)
            row += 1

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('RVIE')

        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:AJ', 22)
        worksheet.set_column('N:N', 40)
        worksheet.set_row(0, 50)

        self._write_headers_report(workbook, worksheet)
        self._write_rows_report(workbook, worksheet, self.processed_results)

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        return 'Reporte de ventas {} {}{}.xlsx'.format(
            self.obj.company_id.name,
            self.obj.year,
            self.obj.month
        )


class SireSaleAcceptProposedTxt:
    def __init__(self, obj, processed_results):
        self.obj = obj
        self.processed_results = processed_results

    def __str__(self):
        return "Reporte RVIE - Cuando acepta la propuesta TXT - {}, {}{}".format(
            self.obj.company_id.name,
            self.obj.year,
            self.obj.month
        )

    @staticmethod
    def _get_template_report():
        return '{company_vat}|{company_name}|' \
            '{period}||{invoice_date}||' \
            '{document_type_code}|{invoice_serie}|' \
            '{invoice_correlative}||{partner_identification_code}|' \
            '{partner_vat}|{partner_name}|{s_base_exp}|' \
            '{s_base_og}|{s_base_ogd}|{s_tax_og}|' \
            '{s_tax_ogd}|{s_base_oe}|{s_base_ou}|{s_tax_isc}|' \
            '{s_tax_icbp}|{s_base_ivap}|{s_tax_ivap}|{s_tax_other}|' \
            '{amount_total}|{currency_name}|{exchange_rate}|' \
            '{origin_invoice_date}|{origin_document_type_code}|' \
            '{origin_number_serie}|{origin_number_correlative}||' \
            '{detraction}|\r\n'

    @staticmethod
    def _write_template_report(template, processed_results):
        content = ''
        for dict_result in processed_results:
            content += template.format(
                company_vat=dict_result['company_vat'],
                company_name=dict_result['company_name'],
                period=dict_result['period'],
                invoice_date=dict_result['invoice_date'],
                document_type_code=dict_result['document_type_code'],
                invoice_serie=dict_result['invoice_serie'],
                invoice_correlative=dict_result['invoice_correlative'],
                partner_identification_code=dict_result['partner_identification_code'],
                partner_vat=dict_result['partner_vat'],
                partner_name=dict_result['partner_name'],
                s_base_exp="{0:.2f}".format(dict_result['s_base_exp']),
                s_base_og="{0:.2f}".format(dict_result['s_base_og']),
                s_base_ogd="{0:.2f}".format(dict_result['s_base_ogd']),
                s_tax_og="{0:.2f}".format(dict_result['s_tax_og']),
                s_tax_ogd="{0:.2f}".format(dict_result['s_tax_ogd']),
                s_base_oe="{0:.2f}".format(dict_result['s_base_oe']),
                s_base_ou="{0:.2f}".format(dict_result['s_base_ou']),
                s_tax_isc="{0:.2f}".format(dict_result['s_tax_isc']),
                s_tax_icbp="{0:.2f}".format(dict_result['s_tax_icbp']),
                s_base_ivap="{0:.2f}".format(dict_result['s_base_ivap']),
                s_tax_ivap="{0:.2f}".format(dict_result['s_tax_ivap']),
                s_tax_other="{0:.2f}".format(dict_result['s_tax_other']),
                amount_total="{0:.2f}".format(dict_result['amount_total']),
                currency_name=dict_result['currency_name'],
                exchange_rate="{0:.3f}".format(dict_result['exchange_rate']) if dict_result['exchange_rate'] else '',
                origin_invoice_date=dict_result['origin_invoice_date'],
                origin_document_type_code=dict_result['origin_document_type_code'],
                origin_number_serie=dict_result['origin_number_serie'],
                origin_number_correlative=dict_result['origin_number_correlative'],
                detraction=dict_result['detraction']
            )
        return content

    def get_content(self):
        template = self._get_template_report()
        content = self._write_template_report(template, self.processed_results)
        return content

    def get_filename(self):
        return 'LE{}{}{}00140400{}{}{}12.txt'.format(
            self.obj.company_id.vat,
            self.obj.year,
            self.obj.month,
            self.obj.opportunity_code,
            self.obj.state_send,
            int(bool(self.processed_results))
        )
