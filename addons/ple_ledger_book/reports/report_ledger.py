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
        style_date = workbook.add_format({
            'size': 10,
            'num_format': 'dd/mm/yy',
            'border': 7
        })

        ws = workbook.add_worksheet('Report Ledger')
        ws.set_column('A:A', 5)
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
        ws.set_column('N:N', 40)
        ws.set_column('O:O', 40)
        ws.set_column('P:P', 40)
        ws.set_column('Q:Q', 40)
        ws.set_column('R:R', 40)
        ws.set_column('S:S', 40)
        ws.set_column('T:T', 40)
        ws.set_column('U:U', 40)

        ws.set_row(0, 50)

        ws.write(0, 0, 'Fila', style_column)
        ws.write(0, 1, 'Periodo', style_column)
        ws.write(0, 2, 'CUO', style_column)
        ws.write(0, 3, 'Número correlativo del asiento', style_column)
        ws.write(0, 4, 'Código Cuenta Contable', style_column)
        ws.write(0, 5, 'Código Único de Operación de la Unidad', style_column)
        ws.write(0, 6, 'Código del centro de costos', style_column)
        ws.write(0, 7, 'Tipo de Moneda Origen', style_column)
        ws.write(0, 8, 'Tipo de documento de identidad del emisor', style_column)
        ws.write(0, 9, 'Número de documento de identidad del emisor', style_column)
        ws.write(0, 10, 'Tipo de comprobante de pago', style_column)
        ws.write(0, 11, 'Serie de comprobante de pago', style_column)
        ws.write(0, 12, 'Número de comprobante de pago', style_column)
        ws.write(0, 13, 'Fecha contable', style_column)
        ws.write(0, 14, 'Fecha de vencimiento', style_column)
        ws.write(0, 15, 'Fecha de la operación o emisión', style_column)
        ws.write(0, 16, 'Glosa de la operación registrada', style_column)
        ws.write(0, 17, 'Glosa referencial', style_column)
        ws.write(0, 18, 'Debe', style_column)
        ws.write(0, 19, 'Haber', style_column)
        ws.write(0, 20, 'Dato estructurado', style_column)
        ws.write(0, 21, 'Estado de la operación', style_column)

        i = 1
        for value in self.data:
            ws.write(i, 0, i, style_content)
            ws.write(i, 1, value['period_name'], style_content)
            ws.write(i, 2, value['move_name'], style_content)
            ws.write(i, 3, value['correlative_line'], style_content)
            ws.write(i, 4, value['account_code'], style_content)
            ws.write(i, 5, value['unit_code'], style_content)
            ws.write(i, 6, value['analytic_distribution'], style_content)
            ws.write(i, 7, value['currency_name'], style_content)
            ws.write(i, 8, value['partner_document_type_code'], style_content)
            ws.write(i, 9, value['partner_document_number'], style_content)
            ws.write(i, 10, value['invoice_document_type_code'], style_content)
            ws.write(i, 11, value['invoice_serie'], style_content)
            ws.write(i, 12, value['invoice_correlative'], style_content)
            ws.write(i, 13, value['ml_date'], style_date)
            ws.write(i, 14, value['ml_date_due'], style_date)
            ws.write(i, 15, value['ml_date_issue'], style_date)
            ws.write(i, 16, value['ml_name'], style_content)
            ws.write(i, 17, value['reference'], style_content)
            ws.write(i, 18, value['debit'], style_content)
            ws.write(i, 19, value['credit'], style_content)
            ws.write(i, 20, value['data_structured'], style_content)
            ws.write(i, 21, value['state'], style_content)
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        name = self.obj.date_start.strftime('%Y%m')
        return 'Libro Mayor_{}_{}.xlsx'.format(self.obj.company_id.name, name)


class LedgerReportTxt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        raw = ''
        template = '{period_name}|{move_name}|{correlative_line}|'\
                   '{account_code}|{unit_code}|{analytic_distribution}|'\
                   '{currency_name}|{partner_document_type_code}|'\
                   '{partner_document_number}|{invoice_document_type_code}|{invoice_serie}|'\
                   '{invoice_correlative}|{ml_date}|{ml_date_due}|'\
                   '{ml_date_issue}|{ml_name}|{reference}|'\
                   '{debit}|{credit}|{data_structured}|{state}|\r\n'
        for value in self.data:
            text = value['analytic_distribution'].split()
            initials=""
            for word in text:
                text_clean = ''.join(character for character in word if character.isalpha())        
                if text_clean:
                    initials += text_clean[0].upper()
            raw += template.format(
                period_name=value['period_name'],
                move_name=value['move_name'],
                correlative_line=value['correlative_line'],
                account_code=value['account_code'],
                unit_code=value['unit_code'],
                analytic_distribution=initials,

                currency_name=value['currency_name'],
                partner_document_type_code=value['partner_document_type_code'],
                partner_document_number=value['partner_document_number'],
                invoice_document_type_code=value['invoice_document_type_code'],
                invoice_serie=value['invoice_serie'],

                invoice_correlative=value['invoice_correlative'],
                ml_date=value['ml_date'],
                ml_date_due=value['ml_date_due'],
                ml_date_issue=value['ml_date_issue'],
                ml_name=value['ml_name'] if value['ml_name'] else value['move_name'],

                reference=value['reference'] if value['reference'] else value['move_name'],
                debit=value['debit'],
                credit=value['credit'],
                data_structured=value['data_structured'],
                state=value['state']
            )
        return raw

    def get_filename(self, type='01'):
        year, month = self.obj.date_start.strftime('%Y/%m').split('/')
        return 'LE{vat}{period_year}{period_month}0006010000{state_send}{has_info}{currency}1.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            state_send=self.obj.state_send or '',
            currency='1' if self.obj.company_id.currency_id.name == 'PEN' else '2',
            has_info=int(bool(self.data))
        )
