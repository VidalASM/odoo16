import copy


class ReportTXTPLE(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data
        self.indicator = None

    def get_content(self):
        raw = ''
        for value in self.data:
            data_value = self.data[value][0]
            data_txt_dict = copy.deepcopy(data_value['data_txt_dict'])
            for line in data_txt_dict:
                balance_value = line['balance']
                if balance_value:
                    formatted_balance = "{:.2f}".format(float(balance_value))
                else:
                    formatted_balance = '0.00'
                raw += data_value['period'][:4] + '0000|' + data_value['code'] + '|' + line['code'] + '|' + str(formatted_balance) + '|' + data_value['indicador'] + '|' + '\r\n'
        self.indicator = raw != ''
        return raw

    def get_filename(self):
        return 'LE{ruc}{date}031800{code_opt_EEFF}{state_send}{indicator}11.txt'.format(
            ruc=self.obj.company_id.vat,
            date=self.obj.date_end.strftime('%Y%m%d'),
            code_opt_EEFF=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send,
            indicator='1' if self.indicator else '0',
        )
