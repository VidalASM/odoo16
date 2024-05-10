from odoo.tests.common import TransactionCase


class TestRucValidationPurchase(TransactionCase):

    def setUp(self):
        super(TestRucValidationPurchase, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Supplier',
            'l10n_latam_identification_type_id': self.env.ref('l10n_pe.it_RUC').id,
            'vat': '20100055519',
            'condition_contributor_sunat': 'HABIDO',
            'state_contributor_sunat': 'ACTIVO',
        })
        self.purchase = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
        })

    def test_purchase_order_ruc_validation(self):
        self.purchase.action_ruc_validation_sunat()
        self.assertEqual(self.po.active_and, 'done')
        print('--------------------------------VALIDATION TEST 1 OK------------------------------')

        # test case where the partner is not registered as HABIDO and ACTIVO
        self.partner.write({
            'condition_contributor_sunat': 'NO HABIDO',
            'state_contributor_sunat': 'NO ACTIVO',
        })
        self.purchase.action_ruc_validation_sunat()
        self.assertEqual(self.purchase.active_and, 'blocked')
        print('--------------------------------VALIDATION TEST 2 OK------------------------------')
