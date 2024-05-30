import base64

from odoo.tests import tagged
from odoo.tools import misc
from odoo.modules import module as modules
from odoo.addons.account_edi.tests.common import AccountEdiTestCommon

@tagged('post_install', '-at_install')
class TestInvoiceValidationByDocument(AccountEdiTestCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref='l10n_pe.pe_chart_template', edi_format_ref='l10n_pe_edi.edi_pe_ubl_2_1'):
        super().setUpClass(chart_template_ref=chart_template_ref, edi_format_ref=edi_format_ref)

        cls.env.ref('base.USD').name = "OLD_USD"
        cls.currency_data['currency'].name = 'USD'

        resource_path = modules.get_resource_path('l10n_pe_edi', 'demo/certificates', 'certificate.pfx')

        cls.certificate = cls.env['l10n_pe_edi.certificate'].create({
            'content': base64.encodebytes(misc.file_open(resource_path, 'rb').read()),
            'password': '12345678a',
        })
        cls.certificate.write({
            'date_start': '2016-01-01 01:00:00',
            'date_end': '2018-01-01 01:00:00',
        })

        cls.company_data['company'].write({
            'country_id': cls.env.ref('base.pe').id,
            'l10n_pe_edi_provider': 'digiflow',
            'l10n_pe_edi_certificate_id': cls.certificate.id,
            'l10n_pe_edi_test_env': True,
        })
        cls.company_data['company'].partner_id.write({
            'vat': "20557912879",
            'l10n_latam_identification_type_id': cls.env.ref('l10n_pe.it_RUC').id,
        })
        cls.company_data['default_journal_sale'].l10n_latam_use_documents = True


        cls.tax_group = cls.env['account.tax.group'].create({
            'name': "IGV",
            'l10n_pe_edi_code': "IGV",
        })
        cls.tax_18 = cls.env['account.tax'].create({
            'name': 'tax_18',
            'amount_type': 'percent',
            'amount': 18,
            'l10n_pe_edi_tax_code': '1000',
            'l10n_pe_edi_unece_category': 'S',
            'type_tax_use': 'sale',
            'tax_group_id': cls.tax_group.id,
        })

        cls.product = cls.env['product.product'].create({
            'name': 'product_pe',
            'weight': 2,
            'uom_po_id': cls.env.ref('uom.product_uom_kgm').id,
            'uom_id': cls.env.ref('uom.product_uom_kgm').id,
            'lst_price': 1000.0,
            'property_account_income_id': cls.company_data['default_account_revenue'].id,
            'property_account_expense_id': cls.company_data['default_account_expense'].id,
            'unspsc_code_id': cls.env.ref('product_unspsc.unspsc_code_01010101').id,
        })

        cls.partner_a.write({
            'vat': '20462509236',
            'l10n_latam_identification_type_id': cls.env.ref('l10n_pe.it_RUC').id,
            'country_id': cls.env.ref('base.pe').id,
        })

        cls.document_type_model = cls.env['l10n_latam.identification.type']
        cls.res_users = cls.env['res.users']

    def test_post_invoice(self):
        vals = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_a.id,
            'invoice_date': '2023-01-17',
            'date': '2023-01-17',
            'currency_id': self.currency_data['currency'].id,
            'l10n_latam_document_type_id': self.env.ref('l10n_pe.document_type01').id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.env.ref('uom.product_uom_kgm').id,
                'price_unit': 2000.0,
                'quantity': 5,
                'discount': 20.0,
                'tax_ids': [(6, 0, self.tax_18.ids)],
            })],
        })
        vals.action_post()
        print('--------------- TEST OK ----------------')