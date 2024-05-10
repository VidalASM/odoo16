from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'
        
    def calculate_iva(self):
        total_iva = self.amount_total / 11.0
        return round(total_iva, 2)