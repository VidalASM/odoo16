from odoo import fields
from datetime import date
from odoo.tests import common

#docker exec -it 160-odoo-1 /bin/bash
# cd opt/odoo_dir/odoo/
#./odoo-bin -c /etc/odoo/odoo.conf -i l10n_pe_format_efact --test-enable -p 8065 -d Mig_taller_sept --stop-after-init
class TestAccountMove(common.TransactionCase):
    def setUp(self):
        super(TestAccountMove, self).setUp()
        self.model_move = self.env['account.move']
        self.model_line = self.env['account.move.line']
        self.model_account = self.env['account.account']
        self.currency_id_pen = self.env['res.currency'].search(
            [('name', '=', 'PEN')]
        )
        self.currency_id_usd = self.env['res.currency'].search(
            [('name', '=', 'USD')]
        )
        self.account_tax_group_id = self.env['account.tax.group'].create({
            'name': 'Grupo Impuesto - Test',
            'sequence': 2,
            'l10n_pe_edi_code': 'IGV'
        })

        self.account_tax_id = self.env['account.tax'].create({
            'name': 'Impuesto - Test',
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'company_id': self.env.ref("base.main_company").id,
            'sequence': 1,
            'amount': 20.0000,
            'tax_group_id': self.account_tax_group_id.id
        })

        self.product_tem = self.env['product.template'].create({
            'name': 'prod_1',
            'global_discount': True,
        })

        self.obj_product = self.env['product.product'].create({
            'name': 'product1',
            'lst_price': 100,
            'product_tmpl_id': self.product_tem.id,
        })

        self.journal_id_usd = self.env['account.journal'].create({
            'name': 'Diario Venta',
            'type': 'sale',
            'code': 'TestD',
            'currency_id': self.currency_id_usd.id
        })

        self.model_01 = self.model_move.create({
            'date': date.today(),
            'move_type': 'out_invoice',
            'company_id': self.env.ref("base.main_company").id,
            'journal_id': self.journal_id_usd.id,
            'currency_id': self.currency_id_usd.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.obj_product.id,
                'price_unit': 50.0,
                'debit': 50.50,
                'credit': 0.50,
                'amount_currency': 50.00,
                'currency_id': self.currency_id_pen.id,
            })],
        })

    def test_resdays(self):
        move = self.model_move.create({
            'invoice_date': '2023-01-01',
            'invoice_date_due': '2023-01-31',
        })
        res = move.resdays()
        self.assertEqual(res, 30, "El número de días debe ser igual a 30")
        print("--- Test test_resdays  OK ---")

    def test_subtotal(self):
        self.assertEqual(self.model_01.subtotal(), 42.37)
        print("--- Test test_subtotal  OK ---")

    def test_total_discount(self):
        model_01 = self.model_move.create({
            'date': date.today(),
            'move_type': 'out_invoice',
            'company_id': self.env.ref("base.main_company").id,
            'journal_id': self.journal_id_usd.id,
            'currency_id': self.currency_id_usd.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.obj_product.id,
                'price_unit': 50.0,
                'debit': 50.50,
                'credit': 0.50,
                'amount_currency': 50.00,
                'currency_id': self.currency_id_pen.id,
                'tax_ids': [(6, 0, [self.account_tax_id.id])],
                'discount': 10.0,
            })],
        })

        self.assertEqual(model_01.total_discount(), 4.167000000000001)
        print("--- Test test_total_discount  OK ---")

    def test_taxes_efact(self):
        self.assertEqual(self.model_01.taxes_efact(), [[42.37, 0, 0, 0, 0]])
        print('--- TEST test_taxes_efact OK  ---')

    def test_efact(self):
        data = self.model_01.taxes_efact()
        efact1 = data[0][0]
        efact2 = data[0][1]
        efact3 = data[0][2]
        efact4 = data[0][3]
        efact5 = data[0][4]

        self.assertEqual(efact1, 42.37)
        self.assertEqual(efact2, 0)
        self.assertEqual(efact3, 0)
        self.assertEqual(efact4, 0)
        self.assertEqual(efact5, 0)
        print('--- TEST test_efact OK  ---')