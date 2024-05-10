from odoo.tests import tagged
from odoo.tests.common import TransactionCase

@tagged('-at_install', 'post_install')
class TestL10nPeFormatGUide(TransactionCase):

    @classmethod
    def setUpClass(self):
        super(TestL10nPeFormatGUide, self).setUpClass()
        self.company_temp = self.env['res.company'].create({
            'name': 'Company test',
        })
        self.company_temp_2 = self.env['res.company'].create({
            'name': 'Company test 2',
        })
        self.account_account_temp = self.env['account.account'].create({
            'account_type': 'asset_cash',
            'code': 'codetest',
            'company_id': self.company_temp.id,
            'create_asset': 'draft',
            'name': 'account test name'
        })
        self.partner_temp = self.env['res.partner'].create({
            'property_account_receivable_id': self.account_account_temp.id,
            'property_account_payable_id': self.account_account_temp.id,
            'name': 'test',
        })
        self.stock_picking = self.env['stock.picking']
        self.stock_location_dest_id = self.env['stock.location']
        self.stock_location_id = self.env['stock.location']
        self.stock_picking_type_id = self.env['stock.picking.type']
        self.stock_user_logger = self.env['res.users']

    def create_stock_location_dest_id(self):
        temp_stock_location_dest_id = self.stock_location_dest_id.create({
            'name': 'test llegada',
            'usage': 'internal',
            'location_id': 1,
            'active': True,
            'barcode': 'test',
            'posx': 1,
            'posy': 1,
            'posz': 1,
            'company_id': self.company_temp.id,
        })
        return temp_stock_location_dest_id

    def create_stock_location_id(self):
        temp_stock_location_id = self.stock_location_id.create({
            'name': 'test partida',
            'usage': 'internal',
            'location_id': 1,
            'active': True,
            'barcode': 'test',
            'posx': 2,
            'posy': 2,
            'posz': 2,
            'company_id': self.company_temp_2.id,
        })
        return temp_stock_location_id

    def create_stock_picking_type_id(self):
        temp_stock_picking_type_id = self.stock_picking_type_id.create({
            'name': 'test stock type',
            'code': 'internal',
            'create_backorder': 'always',
            'reservation_method': 'manual',
            'sequence_code': 'testSequenceCode',
            'active': True,
            'company_id': self.company_temp.id,
        })
        return temp_stock_picking_type_id

    def create_stock_user_logger(self):
        temp_stock_user_logger = self.stock_user_logger.create({
            'name': 'test user',
            'password': 'test password',
            'login': 'login test',
            'notification_type': 'email',
            'company_id': self.company_temp.id,
            'partner_id': self.partner_temp.id,
            'property_account_receivable_id': self.account_account_temp.id,
            'property_account_payable_id': self.account_account_temp.id,
            'company_ids': [(6, 0, [self.company_temp.id, self.company_temp_2.id])]
        })
        return temp_stock_user_logger

    def create_stock_picking(self):
        temp_stock_picking = self.stock_picking.create({
            'name': 'test stock picking',
            'partner_id': self.partner_temp.id,
            'location_dest_id': self.create_stock_location_dest_id().id,
            'location_id': self.create_stock_location_id().id,
            'picking_type_id': self.create_stock_picking_type_id().id,
            'state': 'draft',
            'move_type': 'direct',
            'user_logger': self.create_stock_user_logger().id,
            'weight': 5.0,
            'gross_weight': 10.0,
            'volume': 15.0,
            # 'move_lines': 'stock.move' #one2many
        })
        return temp_stock_picking

    def test_stock_picking(self):
        temp_stock_picking = self.create_stock_picking()
        self.assertEqual(temp_stock_picking.name, 'test stock picking')
        self.assertEqual(temp_stock_picking.state, 'draft')
        self.assertEqual(temp_stock_picking.move_type, 'direct')
        print("----------------------------------------------------TEST PARTE 1 OK----------------------------------------------------")

        report_action = self.env.ref('l10n_pe_format_guide.action_report_guide')
        result = report_action.report_action(temp_stock_picking)
        context_data = result.get('context', {})
        active_ids = context_data.get('active_ids', [])

        self.assertEqual(result.get('type'), 'ir.actions.report')
        self.assertEqual(result.get('report_name'), 'l10n_pe_format_guide.report_guide')
        self.assertEqual(result.get('report_type'), 'qweb-pdf')
        self.assertEqual(result.get('report_file'), 'l10n_pe_format_guide.report_guide')
        self.assertEqual(result.get('name'), 'Guia Fisica')
        self.assertTrue(active_ids)
        print("----------------------------------------------------TEST PARTE 2 OK----------------------------------------------------")