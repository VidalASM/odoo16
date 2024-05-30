from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    means_payment_id = fields.Many2one(default=False)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    means_payment_id = fields.Many2one(default=False)


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    means_payment_id = fields.Many2one(
        comodel_name='payment.methods.codes',
        string="Medio de pago - libro de bancos",
        default=lambda self: self._get_default_means_payment()
    )

    def _get_default_means_payment(self):
        means_payment_id = self.env['payment.methods.codes'].search([('code', '=', '003')])
        if means_payment_id:
            return means_payment_id.id
