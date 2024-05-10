class ReportTXTPLE(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        raw = ''
        template = '{period}|{catalog_code}|{financial_code}|{balance}|{state}|\r\n'

        for value in self.data:
            raw += template.format(
                period=value['period'],
                catalog_code=value['catalog_code'],
                financial_code=value['financial_code'],
                balance="{:.2f}".format(value['balance']),
                state=value['state'],
            )
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}032000{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data))
        )
