from odoo import fields, models,api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    ple_selection = fields.Selection(
        selection_add=[
            ("cash", "1.1 Libro Caja y Bancos: Efectivo"),
            ("bank", "1.2 Libro Caja y Bancos: Cuentas corrientes")]
    )
    bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Cuenta Bancaria'
    )
    
class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_default_means_payment(self):
        means_payment_id = self.env['payment.methods.codes'].search([('code', '=', '003')])
        if means_payment_id:
            return means_payment_id.id

    means_payment_id = fields.Many2one(
        comodel_name='payment.methods.codes',
        string="Medio de pago - libro de bancos",
        default=lambda self: self._get_default_means_payment()
    )
    
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    inv = fields.Boolean(string="Invisible",  store=False)

    def _get_default_means_payment(self):
        means_payment_id = self.env['payment.methods.codes'].search([('code', '=', '003')])
        if means_payment_id:
            return means_payment_id.id
        
    @api.onchange('journal_id')
    def _onchange_journal_id(self):        
        if self.journal_id.type == 'cash':            
            self.inv = False
        else:          
            self.inv = True
        
    means_payment_id = fields.Many2one(
        comodel_name='payment.methods.codes',
        string="Medio de pago - libro de bancos",
        default=lambda self: self._get_default_means_payment()
    )
        
    def _create_payment_vals_from_batch(self, batch_result):
        values = super()._create_payment_vals_from_batch(batch_result)
        values = {'means_payment_id': self._context.get('means_payment_id'), **values}
        return values

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        payment_vals['means_payment_id'] = self.means_payment_id.id
        return payment_vals