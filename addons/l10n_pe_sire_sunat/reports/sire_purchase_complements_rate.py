

class SirePurchaseComplementsRateTxt:
    def __init__(self, obj, processed_results):
        self.obj = obj
        self.processed_results = processed_results

    def __str__(self):
        return "Reporte RCE - Información complementaria para informar la divisa distinta a la SBS TXT - {}, {}{}".format(
            self.obj.company_id.name,
            self.obj.year,
            self.obj.month
        )

    @staticmethod
    def _get_template_report():
        return '{period}|{date}|{currency_name}|{inverse_company_rate}||\r\n'

    @staticmethod
    def _write_template_report(template, processed_results):
        content = ''
        for dict_result in processed_results:
            content += template.format(
                period=dict_result['period'],
                date=dict_result['date'],
                currency_name=dict_result['currency_name'],
                inverse_company_rate=dict_result['inverse_company_rate']
            )
        return content

    def get_content(self):
        template = self._get_template_report()
        content = self._write_template_report(template, self.processed_results)
        return content

    def get_filename(self):
        return '{}-RCETCA-{}{}-{}.txt'.format(
            self.obj.company_id.vat,
            self.obj.year,
            self.obj.month,
            self.obj.correlative if self.obj.correlative else ''
        )
