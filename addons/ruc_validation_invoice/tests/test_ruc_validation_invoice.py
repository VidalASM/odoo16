from odoo import fields
from odoo.tests.common import TransactionCase


class TestRucValidationInvoice(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestRucValidationInvoice, self).setUp(*args, **kwargs)
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'l10n_latam_identification_type_id': self.env.ref('l10n_pe.it_RUC').id,
            'vat': '20123456789',
            'state_contributor_sunat': 'ACTIVO',
            'condition_contributor_sunat': 'HABIDO'
        })
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'service',
            'list_price': 100})
        self.invoice_type = self.env['l10n_latam.document.type'].create({
            'name': 'Invoice',
            'code': '01',
            'country_id': self.env.ref('base.pe').id,
            'require_validation_ruc': True
        })
        return result

    def test_action_ruc_validation_sunat(self):
        account = self.env['account.account'].search([], limit=1)
        invoice = self.env['account.move'].create({
            'partner_id': self.partner.id,
            'l10n_latam_document_type_id': self.invoice_type.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {'product_id': self.product.id,
                                         'quantity': 1,
                                         'account_id': account.id,
                                         'price_unit': 100})]
        })
        invoice.action_ruc_validation_sunat()

        self.assertEqual(invoice.active_and, 'done')
        print('------------------------- VALIDATION - TEST - OK -------------------------------')