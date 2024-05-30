import base64
import os
import tempfile
import zipfile


class ReportInvBalTxt(object):

    def __init__(self, name, line, data, data_2, bank):
        self.name = name
        self.line = line
        self.data = data
        self.data_2 = data_2
        self.bank = bank
        self.filename = 'Pago'

    def get_content(self):
        raw = ''
        if self.bank == '11':
            zeros = '000000000000000000'
            raw += '750{bank_account_id}{currency_id}{amount_total}{process_type}{date}{executing_schedule}{reference}{lines}{validate_belonging}{zeros}\r\n'.format(
                bank_account_id=self.line['bank_account_id'],
                currency_id=self.line['currency_id'],
                amount_total=self.line['amount_total'],
                process_type=self.line['process_type'],
                date=self.line['date'],
                executing_schedule=self.line['executing_schedule'],
                reference=self.line['reference'],
                lines=self.line['lines'],
                validate_belonging=self.line['validate_belonging'],
                zeros=self.line['zeros'],
            )
            template = '002{name}{vat}{bank}{account}{name_client}{amount}{document}{ref}{N}{payment_name}{zeros}\r\n'
            for value in self.data:
                raw += template.format(
                    name=value['name'],
                    vat=value['vat'],
                    bank=value['bank'],
                    account=value['account'],
                    name_client=value['name_client'],
                    amount=value['amount'],
                    document=value['document'],
                    ref=value['ref'],
                    N=value['N'],
                    payment_name=value['payment_name'],
                    zeros=value['zeros']
                )
            return raw
        elif self.bank == '02':
            raw += '{id}{lines_total}{date}{c}{currency}{acc_number}{amount_total}{reference}{N}{abono}\r\n'.format(
                id=self.line['id'],
                lines_total=self.line['lines_total'],
                date=self.line['date'],
                c=self.line['c'],
                currency=self.line['currency'],
                acc_number=self.line['acc_number'],
                amount_total=self.line['amount_total'],
                reference=self.line['reference'],
                N=self.line['N'],
                abono=self.line['abono'],
            )
            template = '{id}{bank_cod}{account}{id_2}{doc}{vat}{spaces}{ref}{reference}{currency}{amount}{N}\r\n'
            for value in self.data:
                raw += template.format(
                    id=value['id'],
                    bank_cod=value['bank_cod'],
                    account=value['account'],
                    id_2=value['id_2'],
                    doc=value['doc'],
                    vat=value['vat'],
                    spaces=value['spaces'],
                    ref=value['ref'],
                    reference=value['reference'],
                    currency=value['currency'],
                    amount=value['amount'],
                    N=value['N'],
                )
            template_2 = '{id}{document}{ref}{amount}\r\n'
            for value in self.data_2:
                raw += template_2.format(
                    id=value['id'],
                    document=value['document'],
                    ref=value['ref'],
                    amount=value['amount'],
                )
            return raw
        elif self.bank == '03':
            raw += '0103{company_code}{service_code}{bank_account}{account_type}{currency_id}{pay}{date_time}{process_type_itb}{date}{lines}{amount_total_pen}{amount_total_usd}{m}\r\n'.format(
                company_code=self.line['company_code'],
                service_code=self.line['service_code'],
                bank_account=self.line['bank_account'],
                account_type=self.line['account_type'],
                currency_id=self.line['currency_id'],
                pay=self.line['pay'],
                date_time=self.line['date_time'],
                process_type_itb=self.line['process_type_itb'],
                date=self.line['date'],
                lines=self.line['lines'],
                amount_total_pen=self.line['amount_total_pen'],
                amount_total_usd=self.line['amount_total_usd'],
                m=self.line['m'],
            )
            template = '02{ruc}{doc}{payment}{currency}{amount}{space}{sunat_bank_code}{account_type}' \
                       '{currency_id}{acc_3}{account}{type_document}{doc_tyoe}{document}{name}{number}\r\n'
            for value in self.data:
                raw += template.format(
                    ruc=value['ruc'],
                    doc=value['doc'],
                    payment=value['payment'],
                    currency=value['currency'],
                    amount=value['amount'],
                    space=value['space'],
                    sunat_bank_code=value['sunat_bank_code'],
                    account_type=value['account_type'],
                    currency_id=value['currency_id'],
                    acc_3=value['acc_3'],
                    account=value['account'],
                    type_document=value['type_document'],
                    doc_tyoe=value['doc_tyoe'],
                    document=value['document'],
                    name=value['name'],
                    number=value['203'],
                )
            return raw
        elif self.bank == '09':
            template = '{ruc}{name}{ref}{invoice_date}{type_acc}{acc_number}' \
                       '{count_account}{cci_number}{space}{currency_id}01\r\n'
            for value in self.data:
                raw += template.format(
                    ruc=value['ruc'],
                    name=value['name'],
                    ref=value['ref'],
                    invoice_date=value['invoice_date'],
                    type_acc=value['type_acc'],
                    acc_number=value['acc_number'],
                    count_account=value['count_account'],
                    cci_number=value['cci_number'],
                    space=value['space'],
                    currency_id=value['currency_id'],
                )
        elif self.bank == '09_txt':
            template = '{ruc}{name}{email}{ref}{currency_id}{amount}' \
                       '{spaces}{bank}\r\n'
            for value in self.data:
                raw += template.format(
                    ruc=value['ruc'],
                    name=value['name'],
                    email=value['email'],
                    ref=value['ref'],
                    currency_id=value['currency_id'],
                    amount=value['amount'],
                    spaces=value['spaces'],
                    bank=value['bank'],
                )
        elif self.bank == '09_zip':
            template = '{ruc}{name}{email}{ref}{currency_id}{amount}' \
                       '{spaces}{bank}\r\n'
            for value in self.data:
                raw += template.format(
                    ruc=value['ruc'],
                    name=value['name'],
                    email=value['email'],
                    ref=value['ref'],
                    currency_id=value['currency_id'],
                    amount=value['amount'],
                    spaces=value['spaces'],
                    bank=value['bank'],
                )
            tmp_dir = self.generate_tmp_dir(raw)
            zip_dir = self.generate_zip(tmp_dir)
            f = open(zip_dir, "rb").read()
            return base64.encodebytes(f)
        return raw

    def get_filename(self):
        if self.bank == '03':
            return 'H2HH03{company_code}{service_code}{count_txt}{date_time}.txt'.format(
                company_code=self.name['company_code'],
                service_code=self.name['service_code'],
                count_txt=self.name['count_txt'],
                date_time=self.name['date_time'],
            )
        else:
            return '{name}.txt'.format(
                name=self.name['name']
            )

    @staticmethod
    def generate_tmp_dir(xmlstr):
        tmp_dir = tempfile.mkdtemp()
        with open(os.path.join(tmp_dir, 'Pago.txt'), 'w') as f:
            f.write(xmlstr)
        return tmp_dir

    def generate_zip(self, tmp_dir):
        zip_filename = os.path.join(tmp_dir, self.filename)
        with zipfile.ZipFile(zip_filename, 'w') as docx:
            docx.write(os.path.join(tmp_dir, 'Pago.txt'), 'Pago.txt')
        return zip_filename
