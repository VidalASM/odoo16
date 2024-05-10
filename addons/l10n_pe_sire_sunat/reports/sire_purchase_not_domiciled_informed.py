from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class SirePurchaseNotDomiciledInformedXlsx:
    def __init__(self, obj, processed_results):
        self.obj = obj
        self.processed_results = processed_results

    def __str__(self):
        return "Reporte RCE no domiciliados - Informado XLSX - {}, {}{}".format(
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
        worksheet.write(0, 1, 'Periodo', style_header)
        worksheet.write(0, 2, 'CAR SUNAT', style_header)
        worksheet.write(0, 3, 'Fecha de Emisión', style_header)
        worksheet.write(0, 4, 'Tipo CP/Doc', style_header)
        worksheet.write(0, 5, 'Serie del CDP', style_header)
        worksheet.write(0, 6, 'Nro CP o Doc', style_header)
        worksheet.write(0, 7, 'Val Adquisiciones', style_header)
        worksheet.write(0, 8, 'Otros', style_header)
        worksheet.write(0, 9, 'Total CP', style_header)
        worksheet.write(0, 10, 'Tipo CP CF', style_header)
        worksheet.write(0, 11, 'Serie CP CF', style_header)
        worksheet.write(0, 12, 'Año', style_header)
        worksheet.write(0, 13, 'Nro CP o Doc. CF', style_header)
        worksheet.write(0, 14, 'Monto Ret', style_header)
        worksheet.write(0, 15, 'Moneda', style_header)
        worksheet.write(0, 16, 'Tipo de Cambio', style_header)
        worksheet.write(0, 17, 'País', style_header)
        worksheet.write(0, 18, 'Apellidos Nombres/ \nRazon Social del sujeto', style_header)
        worksheet.write(0, 19, 'Domicilio', style_header)
        worksheet.write(0, 20, 'ID Sujeto', style_header)
        worksheet.write(0, 21, 'ID Beneficiario', style_header)
        worksheet.write(0, 22, 'Apellidos Nombres/ \nRazon Social del \nbeneficiario', style_header)
        worksheet.write(0, 23, 'País beneficiario', style_header)
        worksheet.write(0, 24, 'Vínculo', style_header)
        worksheet.write(0, 25, 'Rta Bta', style_header)
        worksheet.write(0, 26, 'Deduc/Costo', style_header)
        worksheet.write(0, 27, 'Rta Neta', style_header)
        worksheet.write(0, 28, 'Tasa', style_header)
        worksheet.write(0, 29, 'Impto', style_header)
        worksheet.write(0, 30, 'Convenio', style_header)
        worksheet.write(0, 31, 'Exon.', style_header)
        worksheet.write(0, 32, 'Tipo Rta', style_header)
        worksheet.write(0, 33, 'o Mod Serv', style_header)
        worksheet.write(0, 34, 'Art. 76', style_header)
        worksheet.write(0, 35, 'CAR Orig', style_header)
        worksheet.write(0, 36, '', style_header)

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
            ref_serie = dict_result['ref'].split('-')[0].strip() if '-' in dict_result['ref'] else ''
            ref_correlative = dict_result['ref'].split('-')[1].strip() if '-' in dict_result['ref'] else dict_result['ref'].strip()
            domicile = "{} {}".format(dict_result['partner_street'], dict_result['country_name']).strip()
            worksheet.write(row, 0, row, style_content)
            worksheet.write(row, 1, dict_result['period'], style_content)
            worksheet.write(row, 2, '', style_content)
            worksheet.write(row, 3, dict_result['invoice_date'], style_date)
            worksheet.write(row, 4, dict_result['document_type_code'], style_content)
            worksheet.write(row, 5, ref_serie, style_content)
            worksheet.write(row, 6, ref_correlative, style_content)
            worksheet.write(row, 7, dict_result['p_base_ng'], style_number_two_decimal)
            worksheet.write(row, 8, '', style_content)
            worksheet.write(row, 9, dict_result['p_base_ng'], style_number_two_decimal)
            worksheet.write(row, 10, dict_result['inv_type_document_code'], style_content)
            worksheet.write(row, 11, dict_result['inv_serie'], style_content)
            worksheet.write(row, 12, dict_result['inv_year_dua_dsi'], style_content)
            worksheet.write(row, 13, dict_result['inv_correlative'], style_content)
            worksheet.write(row, 14, dict_result['inv_retention_igv'], style_number_two_decimal)
            worksheet.write(row, 15, dict_result['currency_name'], style_content)
            worksheet.write(row, 16, dict_result['exchange_rate'], style_number_three_decimal)
            worksheet.write(row, 17, dict_result['country_code'], style_content)
            worksheet.write(row, 18, dict_result['partner_name'])
            worksheet.write(row, 19, domicile, style_content)
            worksheet.write(row, 20, dict_result['partner_vat'])
            worksheet.write(row, 21, '', style_content)
            worksheet.write(row, 22, '', style_content)
            worksheet.write(row, 23, '', style_content)
            worksheet.write(row, 24, dict_result['linkage_code'], style_content)
            worksheet.write(row, 25, float(dict_result['hard_rent']), style_number_two_decimal)
            worksheet.write(row, 26, float(dict_result['deduccion_cost']), style_number_two_decimal)
            worksheet.write(row, 27, float(dict_result['neto_rent']), style_number_two_decimal)
            worksheet.write(row, 28, float(dict_result['retention_rate']), style_number_two_decimal)
            worksheet.write(row, 29, float(dict_result['tax_withheld']), style_number_two_decimal)
            worksheet.write(row, 30, dict_result['cdi'], style_content)
            worksheet.write(row, 31, dict_result['exoneration_nodomicilied_code'], style_content)
            worksheet.write(row, 32, dict_result['type_rent_code'], style_content)
            worksheet.write(row, 33, dict_result['taken_code'], style_content)
            worksheet.write(row, 34, dict_result['application_article'], style_content)
            worksheet.write(row, 35, '', style_content)
            row += 1

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('RCE No Domiciliados')

        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:AJ', 22)
        worksheet.set_column('S:S', 40)
        worksheet.set_column('T:T', 30)
        worksheet.set_column('W:W', 40)
        worksheet.set_row(0, 50)

        self._write_headers_report(workbook, worksheet)
        self._write_rows_report(workbook, worksheet, self.processed_results)

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        return 'Reporte de compras no domiciliados {} {}{}.xlsx'.format(
            self.obj.company_id.name,
            self.obj.year,
            self.obj.month
        )


class SirePurchaseNotDomiciledInformedTxt:
    def __init__(self, obj, processed_results):
        self.obj = obj
        self.processed_results = processed_results

    def __str__(self):
        return "Reporte RCE no domiciliados - Informado TXT - {}, {}{}".format(
            self.obj.company_id.name,
            self.obj.year,
            self.obj.month
        )

    @staticmethod
    def _get_template_report():
        return '{period}||{invoice_date}|' \
            '{document_type_code}|{ref_serie}|{ref_correlative}|' \
            '{p_base_ng_1}||{p_base_ng_2}|{inv_type_document_code}|' \
            '{inv_serie}|{inv_year_dua_dsi}|' \
            '{inv_correlative}|{inv_retention_igv}|{currency_name}|' \
            '{exchange_rate}|{country_code}|{partner_name}|' \
            '{domicile}|{partner_vat}||||{linkage_code}|{hard_rent}|' \
            '{deduccion_cost}|{neto_rent}|{retention_rate}|{tax_withheld}|' \
            '{cdi}|{exoneration_nodomicilied_code}|{type_rent_code}|' \
            '{taken_code}|{application_article}||\r\n'

    @staticmethod
    def _write_template_report(template, processed_results):
        content = ''
        for dict_result in processed_results:
            ref_serie = dict_result['ref'].split('-')[0].strip() if '-' in dict_result['ref'] else ''
            ref_correlative = dict_result['ref'].split('-')[1].strip() if '-' in dict_result['ref'] else dict_result['ref'].strip()
            domicile = "{} {}".format(dict_result['partner_street'], dict_result['country_name']).strip()
            content += template.format(
                period=dict_result['period'],
                invoice_date=dict_result['invoice_date'],
                document_type_code=dict_result['document_type_code'],
                ref_serie=ref_serie,
                ref_correlative=ref_correlative,
                p_base_ng_1="{0:.2f}".format(dict_result['p_base_ng']),
                p_base_ng_2="{0:.2f}".format(dict_result['p_base_ng']),
                inv_type_document_code=dict_result['inv_type_document_code'],
                inv_serie=dict_result['inv_serie'],
                inv_year_dua_dsi=dict_result['inv_year_dua_dsi'],
                inv_correlative=dict_result['inv_correlative'],
                inv_retention_igv="{0:.2f}".format(dict_result['inv_retention_igv']),
                currency_name=dict_result['currency_name'],
                exchange_rate="{0:.3f}".format(dict_result['exchange_rate']) if dict_result['exchange_rate'] else '',
                country_code=dict_result['country_code'],
                partner_name=dict_result['partner_name'],
                domicile=domicile,
                partner_vat=dict_result['partner_vat'],
                linkage_code=dict_result['linkage_code'],
                hard_rent=dict_result['hard_rent'].strip(),
                deduccion_cost="{0:.2f}".format(float(dict_result['deduccion_cost'])),
                neto_rent="{0:.2f}".format(float(dict_result['neto_rent'])),
                retention_rate=dict_result['retention_rate'].strip(),
                tax_withheld=dict_result['tax_withheld'].strip(),
                cdi=dict_result['cdi'],
                exoneration_nodomicilied_code=dict_result['exoneration_nodomicilied_code'],
                type_rent_code=dict_result['type_rent_code'],
                taken_code=dict_result['taken_code'],
                application_article=dict_result['application_article']
            )
        return content

    def get_content(self):
        template = self._get_template_report()
        content = self._write_template_report(template, self.processed_results)
        return content

    def get_filename(self):
        return 'LE{}{}{}00080500{}{}{}12.txt'.format(
            self.obj.company_id.vat,
            self.obj.year,
            self.obj.month,
            self.obj.opportunity_code,
            self.obj.state_send,
            int(bool(self.processed_results))
        )
