from odoo import api, fields, models
from num2words import num2words


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _amount_to_text(self):
        """Transform a float amount to text words on peruvian format: AMOUNT IN TEXT 11/100
        :returns: Amount transformed to words peruvian format for invoices
        :rtype: str
        """
        self.ensure_one()
        amount_i, amount_d = divmod(self.amount_total, 1)
        amount_d = int(round(amount_d * 100, 2))
        words = num2words(amount_i, lang='es')
        result = '%(words)s Y %(amount_d)02d/100 %(currency_name)s' % {
            'words': words,
            'amount_d': amount_d,
            'currency_name': self.currency_id.currency_unit_label,
        }
        return result.upper()
