from odoo.tests.common import TransactionCase
from odoo.tests.common import Form


class TestOriginInvoice(TransactionCase):

    def setUp(self):
        super(TestOriginInvoice, self).setUp()
        self.model_move = self.env['account.move']
        model_journal = self.env['account.journal']

        self.obj_company = self.env.user.company_id
        self.obj_partner = self.env.user.partner_id

        self.obj_journal_01 = model_journal.search([
            ('company_id', '=', self.obj_company.id),
            ('type', '=', 'sale')
        ], limit=2)
        self.obj_journal_02 = self.obj_journal_01.copy()
        self.obj_journal_01.invoice_document_type_id = self.env.ref('l10n_pe_catalog.invoice_document_type_factura').id
        self.obj_journal_02.invoice_document_type_id = self.env.ref('l10n_pe_catalog.invoice_document_type_nota_credito').id
        self.obj_reason_cancellation = self.env.ref('l10n_pe_catalog.reason_cancellation_credit_debit_01')

        self.obj_product = self.env['product.product'].create({
            'name': 'product1',
            'lst_price': 100,
        })

    def create_invoice(self, invoice_amount):
        form_move = Form(
            self.model_move.with_context(default_move_type='out_invoice')
        )
        form_move.partner_id = self.obj_partner
        form_move.journal_id = self.obj_journal_01
        with form_move as obj_inv:
            with obj_inv.invoice_line_ids.new() as obj_line:
                obj_line.product_id = self.obj_product
                obj_line.quantity = 3
                obj_line.price_unit = invoice_amount
        obj_invoice = form_move.save()
        return obj_invoice

    def create_invoice_refund(self, invoice):
        context = {
            "active_model": 'account.move',
            "active_ids": [invoice.id],
            "active_id": invoice.id,
            'default_refund_method': 'refund',
        }
        wizard = Form(self.env['account.move.reversal'].with_context(context))
        wizard.journal_id = self.obj_journal_02
        wizard.reason_cancellation_id = self.obj_reason_cancellation
        obj_wizard = wizard.save()
        refund = obj_wizard.reverse_moves()
        obj_credit_note = self.model_move.browse(refund['res_id'])
        return obj_credit_note

    def test_01_validate_refund(self):
        obj_invoice = self.create_invoice(invoice_amount=120)
        obj_invoice.action_post()
        obj_invoice_refund = self.create_invoice_refund(obj_invoice)
        list_predict = [
            obj_invoice_refund.l10n_pe_sunat_code,
            obj_invoice_refund.journal_id.id,
            obj_invoice_refund.origin_move_id.id,
            obj_invoice_refund.origin_serie,
            obj_invoice_refund.origin_invoice_date,
            obj_invoice_refund.origin_inv_document_type_id.id,
            obj_invoice_refund.sunat_origin_code,
            obj_invoice_refund.origin_correlative
        ]
        list_target = [
            '07',
            self.obj_journal_02.id,
            obj_invoice.id,
            obj_invoice.prefix_val,
            obj_invoice.invoice_date,
            obj_invoice.inv_document_type_id.id,
            obj_invoice.l10n_pe_sunat_code,
            obj_invoice.suffix_val
        ]
        self.assertListEqual(list_predict, list_target)
        print('---------TEST OK - VALIDATE DATASET MOVE_REFUND----------')
