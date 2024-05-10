from odoo import models, fields, api, _
import json


class PaymentDetractions(models.TransientModel):
    _name = 'payment.detractions'
    _description = 'Payment massive detractions'

    move_ids = fields.Many2many(
        comodel_name='account.move',
        string='account moves'
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario',
        domain=[('type', '=', 'bank')]
    )
    other_lines = fields.One2many(
        related='journal_id.outbound_payment_method_line_ids'
    )
    outbound_payment_method_line_id = fields.Many2one(
        comodel_name='account.payment.method.line',
        string='Método de pago',
        domain="[('id', 'in', other_lines)]"
    )
    date = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.context_today
    )
    memo = fields.Char(
        string='Memo'
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta de destino'
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        lines = self.env['account.move'].browse(self._context.get('active_ids', []))
        res['move_ids'] = [(6, 0, lines.ids)]
        return res

    def create_payment_account_move(self):
        for move in self.move_ids:
            move_id = self.create_account_move(move)
            payment = self.create_payment(move)
            payment.update({'reference_invoice': move.id})
            payment.update({'move_id': move_id.id})
            payment_to_post = self.env['account.payment'].create(payment)
            payment_to_post.action_post()

    def create_account_move(self, account_move):
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'ref': self.memo,
            'date': self.date,
            'journal_id': self.journal_id.id,
            'currency_id': account_move.currency_id.id,
        })
        return move

    def create_payment(self, move):
        account = False
        
        for line in self.journal_id.outbound_payment_method_line_ids:
            if line.payment_account_id:
                account = line.payment_account_id
        
        if not account:
            account = self.env.company.account_journal_payment_credit_account_id

        exchange_rate = move.to_force_exchange_rate
        if move.currency_id.name != 'PEN':
            currency_exchange = self.env['res.currency'].search([('name', '=', move.currency_id.name), ('active', '=', True)], limit=1)
            for rate in currency_exchange.rate_ids:
                if move.invoice_date == rate.name:
                    exchange_rate = rate.inverse_company_rate
                    break
            if exchange_rate == 0:
                rate_2 = self.env['res.currency.rate'].search([])[0]
                exchange_rate = rate_2.inverse_company_rate

        account_not_found = True
        for line in move.line_ids:
            if line.l10n_pe_is_detraction_retention:
                account_destination = line.account_id.id
                account_not_found = False
                break
        if account_not_found:
            account_destination = move.partner_id.property_account_receivable_id.id

        for bank in self.env.company.partner_id.bank_ids:
            if bank.acc_number == self.journal_id.bank_account_id.acc_number:
                bank_code = bank
                break
            else:
                bank_code = False

        payment_vals = {
            'payment_type': 'outbound',
            'partner_id': move.partner_id.id,
            'amount': self.amount_total_json(move),
            'destination_account_id': account_destination,
            'currency_id': move.currency_id.id,
            'date': self.date,
            'ref': self.memo,
            'journal_id': self.journal_id.id,
            'partner_bank_id': bank_code.id,
            'payment_method_line_id': self.outbound_payment_method_line_id.id,
            'to_force_exchange_rate': exchange_rate,
            'line_ids': [
                (0, 0, {
                    'account_id': account.id if account else False,
                    'partner_id': move.partner_id.id,
                    'name': 'Detracción de la Factura ' + move.name,
                    'amount_currency': float(self.amount_total_json(move)) * (-1),
                    'currency_id': move.currency_id.id,
                    'debit': 0.0,
                    'credit': self.amount_total_json(move) if move.currency_id.name == 'PEN' else float(
                        self.amount_total_json(move)) * exchange_rate,
                }),
                (0, 0, {
                    'account_id': account_destination,
                    'partner_id': move.partner_id.id,
                    'name': 'Detracción de la Factura ' + move.name,
                    'amount_currency': self.amount_total_json(move),
                    'currency_id': move.currency_id.id,
                    'debit': self.amount_total_json(move) if move.currency_id.name == 'PEN' else float(
                        self.amount_total_json(move)) * exchange_rate,
                    'credit': 0.0,
                }),
            ], }
        return payment_vals

    def amount_total_json(self, move):
        amount = float(move.tax_totals['amount_total'])
        for line in move.invoice_line_ids:
            if line.product_id.l10n_pe_withhold_percentage:
                amount = amount * float(line.product_id.l10n_pe_withhold_percentage) / 100
                if move.currency_id.name == 'PEN':
                    amount = round(amount)
                return amount
