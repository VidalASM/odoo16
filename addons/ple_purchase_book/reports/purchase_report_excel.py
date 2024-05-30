from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class PurchaseReportExcel(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def _get_content8_1(self, ws, style_header, style_column, style_number, style_number_bold, style_content, style_date):
        ws.set_column(0, 0, 4)
        ws.set_column(1, 1, 10)
        ws.set_column(2, 2, 14)
        ws.set_column(3, 3, 12)
        ws.set_column(4, 4, 10)
        ws.set_column(5, 5, 10)
        ws.set_column(6, 6, 4)
        ws.set_column(7, 7, 6)
        ws.set_column(8, 8, 8)
        ws.set_column(9, 9, 12)
        ws.set_column(10, 10, 12)
        ws.set_column(11, 11, 4)
        ws.set_column(12, 12, 12)
        ws.set_column(13, 13, 20)
        ws.set_column(14, 14, 17)
        ws.set_column(15, 15, 14)
        ws.set_column(16, 16, 17)
        ws.set_column(17, 17, 14)
        ws.set_column(18, 18, 17)
        ws.set_column(19, 19, 14)
        ws.set_column(20, 20, 17)
        ws.set_column(21, 21, 14)
        ws.set_column(22, 22, 14)
        ws.set_column(23, 23, 17)
        ws.set_column(24, 24, 5)
        ws.set_column(25, 25, 6)
        ws.set_column(26, 26, 10)
        ws.set_column(27, 27, 4)
        ws.set_column(28, 28, 6)
        ws.set_column(29, 29, 8)
        ws.set_column(30, 30, 12)
        ws.set_column(31, 31, 10)
        ws.set_column(32, 32, 14)
        ws.set_column(33, 33, 3)
        ws.set_column(34, 34, 6)
        ws.set_column(35, 35, 8)
        ws.set_column(36, 36, 3)
        ws.set_column(37, 37, 3)
        ws.set_column(38, 38, 3)
        ws.set_column(39, 39, 3)
        ws.set_column(40, 40, 3)
        ws.set_column(41, 41, 3)
        ws.set_column(42, 42, 3)

        header = 0
        total = header + 3
        row_c = total + 1
        row_i = row_c + 1

        ws.write(header, 0, 'Registro de Compras Formato 8.1 de la empresa {}'.format(
            self.obj.company_id.name
        ), style_header)
        ws.write(header + 1, 0, 'Por el periodo comprendio desde el {} al {}'.format(
            self.obj.date_start.strftime('%d/%m/%Y'),
            self.obj.date_end.strftime('%d/%m/%Y')
        ), style_header)

        ws.write(row_c, 0, 'Fila', style_column)
        ws.write(row_c, 1, 'Periodo', style_column)
        ws.write(row_c, 2, 'CUO', style_column)
        ws.write(row_c, 3, 'Correlativo', style_column)
        ws.write(row_c, 4, 'F. Emisión', style_column)
        ws.write(row_c, 5, 'F. V.', style_column)
        ws.write(row_c, 6, 'Tipo Doc.', style_column)
        ws.write(row_c, 7, 'Serie', style_column)
        ws.write(row_c, 8, 'Año DUA', style_column)
        ws.write(row_c, 9, 'Correlativo', style_column)
        ws.write(row_c, 10, 'Número Final', style_column)
        ws.write(row_c, 11, 'T. Doc.', style_column)
        ws.write(row_c, 12, 'N° Doc.', style_column)
        ws.write(row_c, 13, 'Nombre o Razón Social', style_column)
        ws.write(row_c, 14, 'BI Op. Gvds. dest. a op. Grvds.', style_column)
        ws.write(row_c, 15, 'IGV', style_column)
        ws.write(row_c, 16, 'BI Op. Gvds. dest. a op. Mixta', style_column)
        ws.write(row_c, 17, 'IGV', style_column)
        ws.write(row_c, 18, 'BI Op. Gvds dest. a op. No Grvds.', style_column)
        ws.write(row_c, 19, 'IGV', style_column)
        ws.write(row_c, 20, 'Valor Adq. No Gvds.', style_column)
        ws.write(row_c, 21, 'ISC', style_column)
        ws.write(row_c, 22, 'Impuesto consumo de bolsas de plástico', style_column)
        ws.write(row_c, 23, 'Otros', style_column)
        ws.write(row_c, 24, 'Importe Total', style_column)
        ws.write(row_c, 25, 'Moneda', style_column)
        ws.write(row_c, 26, 'T.C.', style_column)
        ws.write(row_c, 27, 'F.E. CP Modificado', style_column)
        ws.write(row_c, 28, 'T. CP. Modificado', style_column)
        ws.write(row_c, 29, 'Serie CP. Modificado', style_column)
        ws.write(row_c, 30, 'DUA', style_column)
        ws.write(row_c, 31, 'Correlativo CP. Modificado', style_column)
        ws.write(row_c, 32, 'F. Deposito Detracción', style_column)
        ws.write(row_c, 33, 'N° Constancia Detracción', style_column)
        ws.write(row_c, 34, 'Retención?', style_column)
        ws.write(row_c, 35, 'Clasificación de Bienes (Tabla 30)', style_column)
        ws.write(row_c, 36, 'Contrato o Proyecto?', style_column)
        ws.write(row_c, 37, 'E.T. 1', style_column)
        ws.write(row_c, 38, 'E.T. 2', style_column)
        ws.write(row_c, 39, 'E.T. 3', style_column)
        ws.write(row_c, 40, 'E.T. 4', style_column)
        ws.write(row_c, 41, 'M. Pago?', style_column)
        ws.write(row_c, 42, 'Estado', style_column)
        ws.write(row_c, 43, 'Libre', style_column)

        ws.set_row(row_c, 33)

        i = 0
        total_base_gdg = 0
        total_tax_gdg = 0
        total_base_gdm = 0
        total_tax_gdm = 0
        total_base_gdng = 0
        total_tax_gdng = 0
        total_amount_untaxed = 0
        total_isc = 0
        total_tax_icbp = 0
        total_another_taxes = 0
        total_amount_total = 0

        for value in self.data:
            if value['voucher_sunat_code'] not in ['91', '97', '98']:
                ws.write(row_i + i, 0, i + 1, style_content)
                ws.write(row_i + i, 1, value['period'], style_content)
                ws.write(row_i + i, 2, value['number_origin'] or '', style_content)
                ws.write(row_i + i, 3, value['journal_correlative'] or '', style_content)
                ws.write(row_i + i, 4, value['date_invoice'] or '', style_date)
                ws.write(row_i + i, 5, value['date_due'] or '', style_date)
                ws.write(row_i + i, 6, value['voucher_sunat_code'] or '', style_content)
                ws.write(row_i + i, 7, value['voucher_series'] or '', style_content)
                ws.write(row_i + i, 8, value['voucher_year_dua_dsi'] or '', style_content)
                ws.write(row_i + i, 9, value['correlative'] or '', style_content)
                ws.write(row_i + i, 10, '', style_content)
                ws.write(row_i + i, 11, value['customer_document_type'] or '', style_content)
                ws.write(row_i + i, 12, value['customer_document_number'] or '', style_content)
                ws.write(row_i + i, 13, value['customer_name'] or '', style_content)
                ws.write(row_i + i, 14, value['base_gdg'], style_number)
                ws.write(row_i + i, 15, value['tax_gdg'], style_number)
                ws.write(row_i + i, 16, value['base_gdm'], style_number)
                ws.write(row_i + i, 17, value['tax_gdm'], style_number)
                ws.write(row_i + i, 18, value['base_gdng'], style_number)
                ws.write(row_i + i, 19, value['tax_gdng'], style_number)
                ws.write(row_i + i, 20, value['amount_untaxed'], style_number)
                ws.write(row_i + i, 21, value['isc'], style_number)
                ws.write(row_i + i, 22, value['tax_icbp'], style_number)
                ws.write(row_i + i, 23, value['another_taxes'], style_number)
                ws.write(row_i + i, 24, value['amount_total'], style_number)
                ws.write(row_i + i, 25, value['code_currency'] or '', style_content)
                ws.write(row_i + i, 26, value['currency_rate'], style_number)
                ws.write(row_i + i, 27, value['origin_date_invoice'] or '', style_date)
                ws.write(row_i + i, 28, value['origin_document_code'] or '', style_content)
                ws.write(row_i + i, 29, value['origin_serie'] or '', style_content)
                ws.write(row_i + i, 30, value['origin_code_aduana'] or '', style_content)
                ws.write(row_i + i, 31, value['origin_correlative'] or '', style_content)
                ws.write(row_i + i, 32, value['voucher_date'] or '', style_date)
                ws.write(row_i + i, 33, value['voucher_number'] or '', style_content)
                ws.write(row_i + i, 34, value['retention'], style_content)
                ws.write(row_i + i, 35, value['class_good_services'] or '', style_content)
                ws.write(row_i + i, 36, value['irregular_societies'] or '', style_content)
                ws.write(row_i + i, 37, value['error_exchange_rate'] or '', style_content)
                ws.write(row_i + i, 38, value['supplier_not_found'] or '', style_content)
                ws.write(row_i + i, 39, value['suppliers_resigned'] or '', style_content)
                ws.write(row_i + i, 40, value['dni_ruc'] or '', style_content)
                ws.write(row_i + i, 41, value['type_pay_invoice'] or '', style_content)
                ws.write(row_i + i, 42, value['ple_state'] or '', style_content)

                total_base_gdg += value['base_gdg']
                total_tax_gdg += value['tax_gdg']
                total_base_gdm += value['base_gdm']
                total_tax_gdm += value['tax_gdm']
                total_base_gdng += value['base_gdng']
                total_tax_gdng += value['tax_gdng']
                total_amount_untaxed += value['amount_untaxed']
                total_isc += value['isc']
                total_tax_icbp += value['tax_icbp']
                total_another_taxes += value['another_taxes']
                total_amount_total += value['amount_total']
                i += 1

        ws.write(total, 14, total_base_gdg, style_number_bold)
        ws.write(total, 15, total_tax_gdg, style_number_bold)
        ws.write(total, 16, total_base_gdm, style_number_bold)
        ws.write(total, 17, total_tax_gdm, style_number_bold)
        ws.write(total, 18, total_base_gdng, style_number_bold)
        ws.write(total, 19, total_tax_gdng, style_number_bold)
        ws.write(total, 20, total_amount_untaxed, style_number_bold)
        ws.write(total, 21, total_isc, style_number_bold)
        ws.write(total, 22, total_tax_icbp, style_number_bold)
        ws.write(total, 23, total_another_taxes, style_number_bold)
        ws.write(total, 24, total_amount_total, style_number_bold)
        return True

    def _get_content8_2(self, ws, style_header, style_column, style_number, style_number_bold, style_content, style_date):
        ws.set_column(0, 0, 4)
        ws.set_column(1, 1, 10)
        ws.set_column(2, 2, 14)
        ws.set_column(3, 3, 12)
        ws.set_column(4, 4, 10)
        ws.set_column(5, 5, 4)
        ws.set_column(6, 6, 6)
        ws.set_column(7, 7, 12)
        ws.set_column(8, 8, 17)
        ws.set_column(9, 9, 14)
        ws.set_column(10, 10, 17)
        ws.set_column(11, 11, 4)
        ws.set_column(12, 12, 6)
        ws.set_column(13, 13, 8)
        ws.set_column(14, 14, 12)
        ws.set_column(15, 15, 14)
        ws.set_column(16, 16, 5)
        ws.set_column(17, 17, 6)
        ws.set_column(18, 18, 10)
        ws.set_column(19, 19, 20)
        ws.set_column(20, 20, 20)
        ws.set_column(21, 21, 12)
        ws.set_column(22, 22, 12)
        ws.set_column(23, 23, 20)
        ws.set_column(24, 24, 12)
        ws.set_column(25, 25, 4)
        ws.set_column(26, 26, 14)
        ws.set_column(27, 27, 14)
        ws.set_column(28, 28, 14)
        ws.set_column(29, 29, 6)
        ws.set_column(30, 30, 14)
        ws.set_column(31, 30, 4)
        ws.set_column(32, 30, 4)
        ws.set_column(33, 30, 4)
        ws.set_column(34, 30, 4)
        ws.set_column(35, 30, 3)
        ws.set_column(36, 30, 3)
        ws.set_column(37, 30, 3)

        header = 0
        total = header + 3
        row_c = total + 1
        row_i = row_c + 1

        ws.write(header, 0, 'Registro de Compras "No domiciliados" Formato 8.2, de la empresa {}'.format(
            self.obj.company_id.name
        ), style_header)
        ws.write(header + 1, 0, 'Por el periodo comprendio desde el {} al {}'.format(
            self.obj.date_start.strftime('%d/%m/%Y'),
            self.obj.date_end.strftime('%d/%m/%Y')
        ), style_header)
        ws.write(row_c, 0, 'Fila', style_column)
        ws.write(row_c, 1, 'Periodo', style_column)
        ws.write(row_c, 2, 'CUO', style_column)
        ws.write(row_c, 3, 'Correlativo', style_column)
        ws.write(row_c, 4, 'F. Emisión', style_column)
        ws.write(row_c, 5, 'Tipo Doc.', style_column)
        ws.write(row_c, 6, 'Serie', style_column)
        ws.write(row_c, 7, 'Correlativo', style_column)
        ws.write(row_c, 8, 'Valor Adquisiciones', style_column)
        ws.write(row_c, 9, 'Otros Conceptos', style_column)
        ws.write(row_c, 10, 'Importe Total', style_column)
        ws.write(row_c, 11, 'Tipo Doc. Origen', style_column)
        ws.write(row_c, 12, 'Serie C.P. Sustento', style_column)
        ws.write(row_c, 13, 'Año DUA', style_column)
        ws.write(row_c, 14, 'Correlativo CP. Sustento.', style_column)
        ws.write(row_c, 15, 'Ret.IGV', style_column)
        ws.write(row_c, 16, 'Moneda', style_column)
        ws.write(row_c, 17, 'T.C.', style_column)
        ws.write(row_c, 18, 'País Residencia', style_column)
        ws.write(row_c, 19, 'Nombre o Razon Social', style_column)
        ws.write(row_c, 20, 'Domicilio en extranjero', style_column)
        ws.write(row_c, 21, 'NIF del extranjero', style_column)
        ws.write(row_c, 22, 'Identificación fiscal beneficiario', style_column)
        ws.write(row_c, 23, 'Nombre o Razon Social beneficiario efectivo de los pagos', style_column)
        ws.write(row_c, 24, 'País residencia del Beneficiario', style_column)
        ws.write(row_c, 25, 'Vínculo', style_column)
        ws.write(row_c, 26, 'Renta Bruta', style_column)
        ws.write(row_c, 27, 'Deducción / Costo venta bienes capital', style_column)
        ws.write(row_c, 28, 'Renta Neta', style_column)
        ws.write(row_c, 29, 'Tasa de retención', style_column)
        ws.write(row_c, 30, 'Impuesto retenido', style_column)
        ws.write(row_c, 31, 'CDI', style_column)
        ws.write(row_c, 32, 'Ex. aplicada', style_column)
        ws.write(row_c, 33, 'Tipo de Renta', style_column)
        ws.write(row_c, 34, 'Modalida', style_column)
        ws.write(row_c, 35, 'Art. 76°?', style_column)
        ws.write(row_c, 36, 'Estado', style_column)
        ws.write(row_c, 37, 'Libre', style_column)

        ws.set_row(row_c, 33)

        i = 0
        total_amount_untaxed = 0
        total_another_taxes = 0
        total_amount_total = 0
        total_inv_retention_igv = 0

        for value in self.data:
            if value['voucher_sunat_code'] in ['91', '97', '98'] and value['partner_nodomicilied'] != '':
                ws.write(row_i + i, 0, i + 1, style_content)
                ws.write(row_i + i, 1, value['period'] or '', style_content)
                ws.write(row_i + i, 2, value['number_origin'] or '', style_content)
                ws.write(row_i + i, 3, value['journal_correlative'] or '', style_content)
                ws.write(row_i + i, 4, value['date_invoice'] or '', style_date)
                ws.write(row_i + i, 5, value['voucher_sunat_code'] or '', style_content)
                ws.write(row_i + i, 6, value['voucher_series'] or '', style_content)
                ws.write(row_i + i, 7, value['correlative'] or '', style_content)
                ws.write(row_i + i, 8, value['amount_untaxed'], style_number)
                ws.write(row_i + i, 9, value['another_taxes'], style_number)
                ws.write(row_i + i, 10, value['rent_neta'].strip(), style_number)
                ws.write(row_i + i, 11, value['l10n_latam_document_type'] if value['l10n_latam_document_type'] != '0' else '', style_content)
                ws.write(row_i + i, 12, value['inv_serie'] or '', style_content)
                ws.write(row_i + i, 13, value['inv_year_dua_dsi'] or '', style_content)
                ws.write(row_i + i, 14, value['inv_correlative'] or '', style_content)
                ws.write(row_i + i, 15, value['inv_retention_igv'] or '0.00', style_number)
                ws.write(row_i + i, 16, value['code_currency'] or '', style_content)
                ws.write(row_i + i, 17, '%.3f' % float(value['currency_rate']), style_number)
                ws.write(row_i + i, 18, value['country_code'] or '', style_content)
                ws.write(row_i + i, 19, value['customer_name'] or '', style_content)
                ws.write(row_i + i, 20, value['partner_street'] or '', style_content)
                ws.write(row_i + i, 21, value['customer_document_number'] or '', style_content)
                ws.write(row_i + i, 22, '', style_content)
                ws.write(row_i + i, 23, '', style_content)
                ws.write(row_i + i, 24, '', style_content)
                ws.write(row_i + i, 25, value['linkage_code'] or '', style_content)
                ws.write(row_i + i, 26, value['hard_rent'].strip(), style_number)
                ws.write(row_i + i, 27, value['deduccion_cost'].strip(), style_number)
                ws.write(row_i + i, 28, value['rent_neta'].strip(), style_number)
                ws.write(row_i + i, 29, value['retention_rate'].strip(), style_number)
                ws.write(row_i + i, 30, value['tax_withheld'].strip(), style_number)
                ws.write(row_i + i, 31, value['cdi'] or '', style_content)
                ws.write(row_i + i, 32, value['exoneration_nodomicilied_code'] or '', style_content)
                ws.write(row_i + i, 33, value['type_rent_code'] or '', style_content)
                ws.write(row_i + i, 34, value['taken_code'] or '', style_content)
                ws.write(row_i + i, 35, value['application_article'] or '', style_content)
                ws.write(row_i + i, 36, value['ple_state'] or '', style_content)

                total_amount_untaxed += value['amount_untaxed']
                total_another_taxes += value['another_taxes']
                total_amount_total += value['amount_total']

                if (value['inv_retention_igv'] == '.00'):
                    inv_retention_igv = 0.00
                elif (value['inv_retention_igv'] == ''):
                    inv_retention_igv = 0.00
                else:
                    inv_retention_igv = value['inv_retention_igv']

                total_inv_retention_igv += inv_retention_igv
                i += 1

        ws.write(total, 8, total_amount_untaxed, style_number_bold)
        ws.write(total, 9, total_another_taxes, style_number_bold)
        ws.write(total, 10, total_amount_total, style_number_bold)
        ws.write(total, 15, total_inv_retention_igv, style_number_bold)
        return True

    def get_content(self, type_report='1'):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        style_header = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
        })
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
        style_number_bold = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
            'bold': True,
            'border': 7
        })
        style_date = workbook.add_format({
            'size': 10,
            'num_format': 'dd/mm/yy',
            'border': 7
        })
        ws = workbook.add_worksheet('Report de Compras')
        if type_report == '1':
            self._get_content8_1(
                ws,
                style_header,
                style_column,
                style_number,
                style_number_bold,
                style_content,
                style_date
            )
        else:
            self._get_content8_2(
                ws,
                style_header,
                style_column,
                style_number,
                style_number_bold,
                style_content,
                style_date
            )

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self, type='01'):
        if type == '01':
            return 'Reporte_compras_8.1.xlsx'
        else:
            return 'Reporte_compras_8.2.xlsx'


class PurchaseReportTxt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data
        self.data8_1 = False
        self.data8_2 = False

    def get_content(self):
        raw = ''
        template = '{period}|{number_origin}|{journal_correlative}|' \
                   '{date_invoice}|{date_due}|{voucher_sunat_code}|' \
                   '{voucher_series}|{voucher_year_dua_dsi}|{correlative}|' \
                   '|{customer_document_type}|{customer_document_number}|' \
                   '{customer_name}|{base_gdg}|{tax_gdg}|{base_gdm}|{tax_gdm}|' \
                   '{base_gdng}|{tax_gdng}|{amount_untaxed}|' \
                   '{isc}|{tax_icbp}|{another_taxes}|{amount_total}|' \
                   '{currency_id}|{invoice_exchange_rate}|' \
                   '{amendment_invoice_date_invoice}|' \
                   '{amendment_invoice_document_type_sunat_code}|' \
                   '{amendment_invoice_voucher_series}|{amendment_code_aduana}|{amendment_invoice_number}|' \
                   '{constancia_deposito_detraccion_fecha_emision}|{constancia_deposito_detraccion_numero}|' \
                   '{retention}|{class_good_services}|{irregular_societies}|{error_exchange_rate}|' \
                   '{supplier_not_found}|{suppliers_resigned}|{dni_ruc}|' \
                   '{pay_invoice_type}|{ple_state}|\r\n'

        for value in self.data:
            if value['voucher_sunat_code'] not in ['91', '97', '98']:
                raw += template.format(
                    period=value['period'],
                    number_origin=value['number_origin'],
                    journal_correlative=value['journal_correlative'],
                    date_invoice=value['date_invoice'],
                    date_due=value['date_due'],

                    voucher_sunat_code=value['voucher_sunat_code'] or '',
                    voucher_series=value['voucher_series'] or '0000',
                    voucher_year_dua_dsi=value['voucher_year_dua_dsi'] or '',
                    correlative=value['correlative'] or '',
                    customer_document_type=value['customer_document_type'] or '',

                    customer_document_number=value['customer_document_number'] or '',
                    customer_name=value['customer_name'] or '',
                    base_gdg='%.2f' % value['base_gdg'],
                    tax_gdg='%.2f' % value['tax_gdg'],
                    base_gdm='%.2f' % value['base_gdm'],

                    tax_gdm='%.2f' % value['tax_gdm'],
                    base_gdng='%.2f' % value['base_gdng'],
                    tax_gdng='%.2f' % value['tax_gdng'],
                    amount_untaxed='%.2f' % value['amount_untaxed'],
                    isc='%.2f' % value['isc'],

                    another_taxes='%.2f' % value['another_taxes'],
                    tax_icbp='%.2f' % value['tax_icbp'],
                    amount_total='%.2f' % value['amount_total'],
                    currency_id=value['code_currency'],
                    invoice_exchange_rate='%.3f' % value['currency_rate'],
                    amendment_invoice_date_invoice=value['origin_date_invoice'],

                    amendment_invoice_document_type_sunat_code=value['origin_document_code'] or '',
                    amendment_invoice_voucher_series=value['origin_serie'] or '',
                    amendment_code_aduana=value['origin_code_aduana'] or '',
                    amendment_invoice_number=value['origin_correlative'] or '',
                    constancia_deposito_detraccion_fecha_emision=value['voucher_date'] or '',

                    constancia_deposito_detraccion_numero=value['voucher_number'] or '',
                    retention=value['retention'] or '',
                    class_good_services=value['class_good_services'] or '',
                    irregular_societies=value['irregular_societies'] or '',
                    error_exchange_rate=value['error_exchange_rate'] or '',
                    supplier_not_found=value['supplier_not_found'] or '',
                    suppliers_resigned=value['suppliers_resigned'] or '',
                    dni_ruc=value['dni_ruc'] or '',
                    pay_invoice_type=value['type_pay_invoice'] or '',
                    ple_state=value['ple_state'] or ''
                )
        if raw:
            self.data8_1 = True
        return raw

    def get_content8_2(self):
        raw = ''
        template = '{period}|{number_origin}|{journal_correlative}|' \
                   '{date_invoice}|{voucher_sunat_code}|{voucher_series}|' \
                   '{correlative}|{amount_untaxed}|{another_taxes}|' \
                   '{amount_total}|{amendment_invoice_document_type_sunat_code}|{amendment_invoice_voucher_series}|' \
                   '{amendment_year_aduana}|{amendment_invoice_number}|{amendment_invoice_retention_igv}|' \
                   '{currency_id}|{invoice_exchange_rate}|{country_code}|' \
                   '{customer_name}|{partner_street}|{customer_document_number}||||' \
                   '{link_partner_beneficiary}|{hard_rent}|{deduccion}|' \
                   '{rent_neta}|{retention_rate}|{retention_tax}|' \
                   '{code_double_taxation_agreement}|{exoneration_nodomicilied}|{type_rent}|' \
                   '{service_taken}|{pre_pay}|{ple_state}|\r\n'

        for value in self.data:
            if value['voucher_sunat_code'] in ['91', '97', '98'] and value['partner_nodomicilied'] != '':
                raw += template.format(
                    period=value['period'],
                    number_origin=value['number_origin'],
                    journal_correlative=value['journal_correlative'],
                    date_invoice=value['date_invoice'],
                    voucher_sunat_code=value['voucher_sunat_code'] or '',
                    voucher_series=value['voucher_series'] or '0000',
                    correlative=value['correlative'] or '',
                    amount_untaxed='%.2f' % value['amount_untaxed'],
                    another_taxes='%.2f' % value['another_taxes'],
                    amount_total='%.2f' % float(value['rent_neta']) if value['rent_neta'] != '' else '0.00',
                    amendment_invoice_document_type_sunat_code=value['l10n_latam_document_type'] if value['l10n_latam_document_type'] != '0' else '',
                    amendment_invoice_voucher_series=value['inv_serie'] or '',
                    amendment_year_aduana=value['inv_year_dua_dsi'],
                    amendment_invoice_number=value['inv_correlative'] or '',
                    amendment_invoice_retention_igv=value['inv_retention_igv'] or '0.00',
                    currency_id=value['code_currency'],
                    invoice_exchange_rate='%.3f' % value['currency_rate'],
                    country_code=value['country_code'] or '',
                    customer_name=value['customer_name'] or '',
                    partner_street=value['partner_street'] or '',
                    customer_document_number=value['customer_document_number'] or '',
                    link_partner_beneficiary=value['linkage_code'] or '',
                    hard_rent=value['hard_rent'].strip(),
                    deduccion='%.2f' % float(value['deduccion_cost']) if value['deduccion_cost'] != '' else '0.00',
                    rent_neta='%.2f' % float(value['rent_neta']) if value['rent_neta'] != '' else '0.00',
                    retention_rate=value['retention_rate'].strip(),
                    retention_tax=value['tax_withheld'].strip(),
                    code_double_taxation_agreement=value['cdi'] or '',
                    exoneration_nodomicilied=value['exoneration_nodomicilied_code'] or '',
                    type_rent=value['type_rent_code'] or '',
                    service_taken=value['taken_code'] or '',
                    pre_pay=value['application_article'] or '',
                    ple_state=value['ple_state'] or ''
                )
        if raw:
            self.data8_2 = True
        return raw

    def get_filename(self, type='01'):
        year, month = self.obj.date_start.strftime('%Y/%m').split('/')
        state_send = self.obj.state_send
        return 'LE{vat}{period_year}{period_month}0008{type}0000{state_send}{has_info}{currency}1.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            type=type,
            currency='1' if self.obj.company_id.currency_id.name == 'PEN' else '2',
            has_info=int(bool(self.data8_1)),
            state_send=state_send
        )

    def get_filename2(self):
        year, month = self.obj.date_start.strftime('%Y/%m').split('/')
        state_send = self.obj.state_send
        return 'LE{vat}{period_year}{period_month}0008020000{state_send}{has_info}{currency}1.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            currency='1' if self.obj.company_id.currency_id.name == 'PEN' else '2',
            has_info=int(bool(self.data8_2)),
            state_send=state_send
        )
