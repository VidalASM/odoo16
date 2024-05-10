from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _check_reconciliation(self):
        for line in self:
            if line.matched_debit_ids or line.matched_credit_ids:
                pass
