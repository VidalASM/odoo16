from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class SirePurchaseAddProposedXlsx:
    def __init__(self, obj, processed_results):
        self.obj = obj
        self.processed_results = processed_results

    def __str__(self):
        return "Reporte RCE - Agregar datos a la propuesta XLSX - {}, {}{}".format(
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
        worksheet.write(0, 9, 'Año', style_header)
        worksheet.write(0, 10, 'Nro CP o \nDoc. Nro Inicial \n(Rango)', style_header)
        worksheet.write(0, 11, 'Nro Final (Rango)', style_header)
        worksheet.write(0, 12, 'Tipo Doc Identidad', style_header)
        worksheet.write(0, 13, 'Nro Doc Identidad', style_header)
        worksheet.write(0, 14, 'Apellidos Nombres/ \nRazón Social', style_header)
        worksheet.write(0, 15, 'BI Gravado DG', style_header)
        worksheet.write(0, 16, 'IGV/IPM DG', style_header)
        worksheet.write(0, 17, 'BI Gravado DGNG', style_header)
        worksheet.write(0, 18, 'IGV/IPM DGNG', style_header)
        worksheet.write(0, 19, 'BI Gravado DNG', style_header)
        worksheet.write(0, 20, 'IGV/IPM DNG', style_header)
        worksheet.write(0, 21, 'Valor Adq. NG', style_header)
        worksheet.write(0, 22, 'ISC', style_header)
        worksheet.write(0, 23, 'ICBPER', style_header)
        worksheet.write(0, 24, 'Otros Trib/Cargos', style_header)
        worksheet.write(0, 25, 'Total CP', style_header)
        worksheet.write(0, 26, 'Moneda', style_header)
        worksheet.write(0, 27, 'Tipo de Cambio', style_header)
        worksheet.write(0, 28, 'Fecha Emisión \nDoc Modificado', style_header)
        worksheet.write(0, 29, 'Tipo CP Modificado', style_header)
        worksheet.write(0, 30, 'Serie CP Modificado', style_header)
        worksheet.write(0, 31, 'COD. DAM O DSI 1', style_header)
        worksheet.write(0, 32, 'Nro CP Modificado', style_header)
        worksheet.write(0, 33, 'Clasif de Bss y Sss', style_header)
        worksheet.write(0, 34, 'ID Proyecto \nOperadores \nPartícipes', style_header)
        worksheet.write(0, 35, 'PorcPart', style_header)
        worksheet.write(0, 36, 'IMB', style_header)
        worksheet.write(0, 37, 'CAR Orig/Ind E o I', style_header)
        worksheet.write(0, 38, 'Detracción', style_header)
        worksheet.write(0, 39, '', style_header)

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
            worksheet.write(row, 6, dict_result['invoice_date_due'], style_date)
            worksheet.write(row, 7, dict_result['document_type_code'], style_content)
            worksheet.write(row, 8, dict_result['ref_serie'], style_content)
            worksheet.write(row, 9, dict_result['year_aduana'], style_content)
            worksheet.write(row, 10, dict_result['ref_correlative'], style_content)
            worksheet.write(row, 11, '', style_content)
            worksheet.write(row, 12, dict_result['partner_identification_code'], style_content)
            worksheet.write(row, 13, dict_result['partner_vat'])
            worksheet.write(row, 14, dict_result['partner_name'])
            worksheet.write(row, 15, dict_result['p_base_gdg'], style_number_two_decimal)
            worksheet.write(row, 16, dict_result['p_tax_gdg'], style_number_two_decimal)
            worksheet.write(row, 17, dict_result['p_base_gdm'], style_number_two_decimal)
            worksheet.write(row, 18, dict_result['p_tax_gdm'], style_number_two_decimal)
            worksheet.write(row, 19, dict_result['p_base_gdng'], style_number_two_decimal)
            worksheet.write(row, 20, dict_result['p_tax_gdng'], style_number_two_decimal)
            worksheet.write(row, 21, dict_result['p_base_ng'], style_number_two_decimal)
            worksheet.write(row, 22, dict_result['p_tax_isc'], style_number_two_decimal)
            worksheet.write(row, 23, dict_result['p_tax_icbp'], style_number_two_decimal)
            worksheet.write(row, 24, dict_result['p_tax_other'], style_number_two_decimal)
            worksheet.write(row, 25, dict_result['amount_total'], style_number_two_decimal)
            worksheet.write(row, 26, dict_result['currency_name'], style_content)
            worksheet.write(row, 27, dict_result['exchange_rate'], style_number_three_decimal)
            worksheet.write(row, 28, dict_result['origin_invoice_date'], style_date)
            worksheet.write(row, 29, dict_result['origin_document_type_code'], style_content)
            worksheet.write(row, 30, dict_result['origin_number_serie'], style_content)
            worksheet.write(row, 31, dict_result['code_aduana'], style_content)
            worksheet.write(row, 32, dict_result['origin_number_correlative'], style_content)
            worksheet.write(row, 33, dict_result['classification_services_code'], style_content)
            worksheet.write(row, 34, '', style_content)
            worksheet.write(row, 35, '', style_content)
            worksheet.write(row, 36, '', style_content)
            worksheet.write(row, 37, '', style_content)
            worksheet.write(row, 38, dict_result['detraction'], style_content)
            row += 1

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('RCE')

        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:AM', 22)
        worksheet.set_column('O:O', 40)
        worksheet.set_row(0, 50)

        self._write_headers_report(workbook, worksheet)
        self._write_rows_report(workbook, worksheet, self.processed_results)

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        return 'Registro de compras {} {}{}.xlsx'.format(
            self.obj.company_id.name,
            self.obj.year,
            self.obj.month
        )


class SirePurchaseAddProposedTxt:
    def __init__(self, obj, processed_results):
        self.obj = obj
        self.processed_results = processed_results

    def __str__(self):
        return "Reporte RCE - Agregar datos a la propuesta TXT - {}, {}{}".format(
            self.obj.company_id.name,
            self.obj.year,
            self.obj.month
        )

    @staticmethod
    def _get_template_report():
        return '{company_vat}|{company_name}|' \
            '{period}||{invoice_date}|' \
            '{invoice_date_due}|{document_type_code}|{ref_serie}|' \
            '{year_aduana}|{ref_correlative}||' \
            '{partner_identification_code}|{partner_vat}|{partner_name}|' \
            '{p_base_gdg}|{p_tax_gdg}|{p_base_gdm}|' \
            '{p_tax_gdm}|{p_base_gdng}|{p_tax_gdng}|{p_base_ng}|' \
            '{p_tax_isc}|{p_tax_icbp}|{p_tax_other}|{amount_total}|' \
            '{currency_name}|{exchange_rate}|{origin_invoice_date}|' \
            '{origin_document_type_code}|{origin_number_serie}|' \
            '{code_aduana}|{origin_number_correlative}|{classification_services_code}|||||' \
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
                invoice_date_due=dict_result['invoice_date_due'],
                document_type_code=dict_result['document_type_code'],
                ref_serie=dict_result['ref_serie'],
                year_aduana=dict_result['year_aduana'],
                ref_correlative=dict_result['ref_correlative'],
                partner_identification_code=dict_result['partner_identification_code'],
                partner_vat=dict_result['partner_vat'],
                partner_name=dict_result['partner_name'],
                p_base_gdg="{0:.2f}".format(dict_result['p_base_gdg']),
                p_tax_gdg="{0:.2f}".format(dict_result['p_tax_gdg']),
                p_base_gdm="{0:.2f}".format(dict_result['p_base_gdm']),
                p_tax_gdm="{0:.2f}".format(dict_result['p_tax_gdm']),
                p_base_gdng="{0:.2f}".format(dict_result['p_base_gdng']),
                p_tax_gdng="{0:.2f}".format(dict_result['p_tax_gdng']),
                p_base_ng="{0:.2f}".format(dict_result['p_base_ng']),
                p_tax_isc="{0:.2f}".format(dict_result['p_tax_isc']),
                p_tax_icbp="{0:.2f}".format(dict_result['p_tax_icbp']),
                p_tax_other="{0:.2f}".format(dict_result['p_tax_other']),
                amount_total="{0:.2f}".format(dict_result['amount_total']),
                currency_name=dict_result['currency_name'],
                exchange_rate="{0:.3f}".format(dict_result['exchange_rate']) if dict_result['exchange_rate'] else '',
                origin_invoice_date=dict_result['origin_invoice_date'],
                origin_document_type_code=dict_result['origin_document_type_code'],
                origin_number_serie=dict_result['origin_number_serie'],
                code_aduana=dict_result['code_aduana'],
                origin_number_correlative=dict_result['origin_number_correlative'],
                classification_services_code=dict_result['classification_services_code'],
                detraction=dict_result['detraction']
            )
        return content

    def get_content(self):
        template = self._get_template_report()
        content = self._write_template_report(template, self.processed_results)
        return content

    def get_filename(self):
        return '{}-CP-{}{}-{}.txt'.format(
            self.obj.company_id.vat,
            self.obj.year,
            self.obj.month,
            self.obj.correlative if self.obj.correlative else ''
        )
