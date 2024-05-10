from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestInvoiceTypeMove(TransactionCase):
        
    def setUp(self):
        super(TestInvoiceTypeMove, self).setUp()
        
        self.ts_account_move = self.env['account.move'].create({
            'serie_correlative':'E003-03'
        })
        
        self.ts_account_move_line = self.env['account.move.line'].create({
            'move_id': self.ts_account_move.id,
            'name': 'ExampleLine',
            'account_id': 3,  
            'debit': 0.00,  
            'credit': 0.00,
            'move_type': 'entry',
            'serie_correlative_is_readonly': False
        })
          
        print("----SETUP OK----")
                
    def test_fields_invoice_account_move(self):
        self.assertEqual(self.ts_account_move_line.move_id.id,self.ts_account_move.id)
        self.assertEqual(self.ts_account_move_line.name,'ExampleLine')
        self.assertEqual(self.ts_account_move_line.account_id.id, 3)
        self.assertEqual(self.ts_account_move_line.debit, 0.00)
        self.assertEqual(self.ts_account_move_line.credit, 0.00)
        self.assertEqual(self.ts_account_move_line.move_type, 'entry')
        self.assertFalse(self.ts_account_move_line.serie_correlative_is_readonly)
        self.assertEqual(self.ts_account_move.serie_correlative, 'E003-03')
        print("-------TEST FIELDS INVOICE OK-----")
    
    def test_function_invoice_move(self):
        self.assertIsNone(self.ts_account_move._compute_serie_correlative_payment())
        self.assertIsNone(self.ts_account_move._compute_name())
        self.assertIsNone(self.ts_account_move_line._compute_serie_correlative_is_readonly())
        print("-------TEST FUNCTION INVOICE OK-----")