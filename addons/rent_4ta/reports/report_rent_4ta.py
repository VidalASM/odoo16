
class ReportRent4ta(object):

    def __init__(self, obj, data_ps4, data_4ta):
        self.obj = obj
        self.data_ps4 = data_ps4
        self.data_4ta = data_4ta

    def get_content_data_ps4(self):
        raw = ''
        template = '{document_type_code}|{document_number}|{first_name}|{second_name}|' \
                   '{partner_name}|{is_nodomicilied}|{double_taxation_code}|\r\n'
        
        for value in self.data_ps4:
            raw += template.format(
                document_type_code=self.data_ps4[value][0]['document_type_code'],
                document_number=self.data_ps4[value][0]['document_number'],
                first_name=self.data_ps4[value][0]['first_name'],
                second_name=self.data_ps4[value][0]['second_name'],
                partner_name=self.data_ps4[value][0]['partner_name'],
                is_nodomicilied=self.data_ps4[value][0]['is_nodomicilied'],
                double_taxation_code=self.data_ps4[value][0]['double_taxation_code']
            )
        return raw
    
    def get_content_data_4ta(self):
        raw = ''
        template = '{document_type_code}|{document_number}|R|{ref_prefix}|' \
                   '{ref_suffix}|{amount_total}|{invoice_date}|{payment_date}|{quarter}|||\r\n'
        
        for value in self.data_4ta:
            raw += template.format(
                document_type_code=value['document_type_code'],
                document_number=value['document_number'],
                ref_prefix=value['ref_prefix'],
                ref_suffix=value['ref_suffix'],
                amount_total=value['amount_total'],
                invoice_date=value['invoice_date'],
                payment_date=value['payment_date'],
                quarter=value['quarter']
            )
        return raw

    def get_filename(self, type):
        year, month, day = self.obj.date_to.strftime('%Y/%m/%d').split('/')
        return '0601{period_year}{period_month}{vat}.{type}'.format(
            period_year=year,
            period_month=month,
            vat=self.obj.company_id.vat[:11] if self.obj.company_id.vat else '00000000000',
            type=type
        )
