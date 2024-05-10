from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class SaleReportExcel(object):

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

        worksheet = workbook.add_worksheet('Report de Venta')
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 40)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:P', 40)
        worksheet.set_column('Q:Q', 10)
        worksheet.set_column('R:X', 20)
        worksheet.set_column('Y:Y', 10)
        worksheet.set_column('AB:AG', 30)
        worksheet.set_column('AH:AH', 20)
        worksheet.set_column('AI:AI', 10)
        worksheet.set_column('AJ:AJ', 30)
        worksheet.set_row(0, 50)

        worksheet.write(0, 0, 'Fila', style1)
        worksheet.write(0, 1, 'Periodo', style1)
        worksheet.write(0, 2, 'Código Único de la \nOperación (CUO) o RER', style1)
        worksheet.write(0, 3, 'Número correlativo del \nasiento contable identificado en el campo 2', style1)
        worksheet.write(0, 4, 'F. emisión', style1)
        worksheet.write(0, 5, 'F. Vto. o Pago', style1)
        worksheet.write(0, 6, 'Tipo Comprobante', style1)
        worksheet.write(0, 7, 'Serie', style1)
        worksheet.write(0, 8, 'Número de comprobante, \no número inicial del consolidado diario', style1)
        worksheet.write(0, 9, 'Número de comprobante, \no número final del consolidado diario', style1)
        worksheet.write(0, 10, 'Tipo Documento Identidad', style1)
        worksheet.write(0, 11, 'Número Documento Identidad', style1)
        worksheet.write(0, 12, 'Apellidos y nombres, \ndenominación o razón social', style1)
        worksheet.write(0, 13, 'Valor facturado exportación', style1)
        worksheet.write(0, 14, 'Base imponible operación \ngravada', style1)
        worksheet.write(0, 15, 'Dscto. Base Imponible', style1)
        worksheet.write(0, 16, 'IGV y/o IPM', style1)
        worksheet.write(0, 17, 'Dscto. IGV y/o IPM', style1)
        worksheet.write(0, 18, 'Importe total operación \nexonerada', style1)
        worksheet.write(0, 19, 'Importe total operación \ninafecta', style1)
        worksheet.write(0, 20, 'ISC', style1)
        worksheet.write(0, 21, 'Base imponible IVAP', style1)
        worksheet.write(0, 22, 'IVAP', style1)
        worksheet.write(0, 23, 'Impuesto consumo de bolsas de plástico', style1)
        worksheet.write(0, 24, 'Otros conceptos, \ntributos y cargos', style1)
        worksheet.write(0, 25, 'Importe total', style1)
        worksheet.write(0, 26, 'Moneda', style1)
        worksheet.write(0, 27, 'T.C.', style1)
        worksheet.write(0, 28, 'F. emisión documento original \nque se modifica', style1)
        worksheet.write(0, 29, 'Tipo comprobante que se modifica', style1)
        worksheet.write(0, 30, 'Serie comprobante de pago \nque se modifica', style1)
        worksheet.write(0, 31, 'Número comprobante de pago \nque se modifica', style1)
        worksheet.write(0, 32, 'Identificación del Contrato \nde colaboración que no \nlleva contabilidad independiente', style1)
        worksheet.write(0, 33, 'Error tipo 1: inconsistencia T.C.', style1)
        worksheet.write(0, 34, '¿Cancelado conmedio de pago?', style1)
        worksheet.write(0, 35, 'Estado PLE', style1)
        worksheet.write(0, 36, 'Campos de libre utilización', style1)

        i = 1
        for value in self.data:
            worksheet.write(i, 0, i)
            worksheet.write(i, 1, value['period'])
            worksheet.write(i, 2, value['number_origin'])
            worksheet.write(i, 3, value['journal_correlative'])
            worksheet.write(i, 4, value['date_invoice'])
            worksheet.write(i, 5, value['date_due'])
            worksheet.write(i, 6, value['voucher_sunat_code'])
            worksheet.write(i, 7, value['voucher_series'])
            worksheet.write(i, 8, value['correlative'])
            worksheet.write(i, 9, value['correlative_end'])
            worksheet.write(i, 10, value['customer_document_type'])
            worksheet.write(i, 11, value['customer_document_number'])
            worksheet.write(i, 12, value['customer_name'])
            worksheet.write(i, 13, value['amount_export'])
            worksheet.write(i, 14, value['amount_untaxed'])
            worksheet.write(i, 15, value['discount_tax_base'])
            worksheet.write(i, 16, value['sale_no_gravadas_igv'])
            worksheet.write(i, 17, value['discount_igv'])
            worksheet.write(i, 18, value['amount_exonerated'])
            worksheet.write(i, 19, value['amount_no_effect'])
            worksheet.write(i, 20, value['isc'])
            worksheet.write(i, 21, value['rice_tax_base'])
            worksheet.write(i, 22, value['rice_igv'])
            worksheet.write(i, 23, value['tax_icbp'], style_number)
            worksheet.write(i, 24, value['another_taxes'])
            worksheet.write(i, 25, value['amount_total'])
            worksheet.write(i, 26, value['code_currency'])
            worksheet.write(i, 27, value['currency_rate'])
            worksheet.write(i, 28, value['origin_date_invoice'])
            worksheet.write(i, 29, value['origin_document_code'])
            worksheet.write(i, 30, value['origin_serie'])
            worksheet.write(i, 31, value['origin_correlative'])
            worksheet.write(i, 32, value['contract_name'])
            worksheet.write(i, 33, value['inconsistency_type_change'])
            worksheet.write(i, 34, value['payment_voucher'])
            worksheet.write(i, 35, value['ple_state'])
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        name = self.obj.date_start.strftime('%Y%m')
        return 'Reporte_ventas_{}_{}.xlsx'.format(self.obj.company_id.name, name)


class SaleReportTxt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        raw = ''
        template = '{period}|{number_origin}|' \
                   '{journal_correlative}|{date_invoice}|{date_due}|' \
                   '{voucher_sunat_code}|{voucher_series}|{correlative}|' \
                   '{correlative_end}|{customer_document_type}|{customer_document_number}|' \
                   '{customer_name}|{amount_export}|{amount_untaxed}|' \
                   '{discount_tax_base}|{sale_no_gravadas_igv}|{discount_igv}|' \
                   '{amount_exonerated}|{amount_no_effect}|{isc}|{rice_tax_base}|' \
                   '{rice_igv}|{tax_icbp}|{another_taxes}|{amount_total}|' \
                   '{code_currency}|{currency_rate}|{amendment_invoice_date_invoice}|' \
                   '{amendment_invoice_voucher_sunat_code}|{amendment_invoice_voucher_series}|' \
                   '{amendment_invoice_correlative}|{contract_name}|' \
                   '{inconsistency_type_change}|{payment_voucher}|{ple_state_sale}|\r\n'

        for value in self.data:
            raw += template.format(
                period=value['period'],
                number_origin=value['number_origin'],
                journal_correlative=value['journal_correlative'],
                date_invoice=value['date_invoice'],
                date_due=value['date_due'],

                voucher_sunat_code=value['voucher_sunat_code'],
                voucher_series=value['voucher_series'],
                correlative=value['correlative'],
                correlative_end=value['correlative_end'],
                customer_document_type=value['customer_document_type'],

                customer_document_number=value['customer_document_number'],
                customer_name=value['customer_name'],
                amount_export=value['amount_export'],
                amount_untaxed=value['amount_untaxed'],
                discount_tax_base=value['discount_tax_base'],

                sale_no_gravadas_igv=value['sale_no_gravadas_igv'],
                discount_igv=value['discount_igv'],
                amount_exonerated=value['amount_exonerated'],
                amount_no_effect=value['amount_no_effect'],
                isc=value['isc'],

                rice_tax_base=value['rice_tax_base'],
                rice_igv=value['rice_igv'],
                tax_icbp=value['tax_icbp'],
                another_taxes=value['another_taxes'],
                amount_total=value['amount_total'],

                code_currency=value['code_currency'],
                currency_rate=value['currency_rate'],
                amendment_invoice_date_invoice=value['origin_date_invoice'],
                amendment_invoice_voucher_sunat_code=value['origin_document_code'],
                amendment_invoice_voucher_series=value['origin_serie'],

                amendment_invoice_correlative=value['origin_correlative'],
                contract_name=value['contract_name'],
                inconsistency_type_change=value['inconsistency_type_change'],
                payment_voucher=value['payment_voucher'],
                ple_state_sale=value['ple_state'],
            )
        return raw

    def get_filename(self, filename_type='01'):
        year, month = self.obj.date_start.strftime('%Y/%m').split('/')
        return 'LE{vat}{period_year}{period_month}0014{filename_type}0000{state_send}{has_info}{currency}1.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            filename_type=filename_type,
            state_send=self.obj.state_send or '',
            currency='1' if self.obj.company_id.currency_id.name == 'PEN' else '2',
            has_info=int(bool(self.data))
        )
