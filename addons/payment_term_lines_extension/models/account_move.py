from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange('invoice_payment_term_id', 'currency_id')
    def _onchange_account_id(self):
        self.ensure_one()
        currency = self.currency_id
        filtered_lines = [line for line in self.line_ids if line.display_type == "payment_term" and line.l10n_pe_is_detraction_retention]

        for payment_term, line in zip(self.invoice_payment_term_id.line_ids, filtered_lines):
            account_id = None
            for term_extension in payment_term.term_extension:
                if term_extension.currency == currency:
                    if self.move_type in ['out_invoice', 'out_refund']:
                        account_id = term_extension.ledger_account
                    elif self.move_type in ['in_invoice', 'in_refund']:
                        account_id = term_extension.ledger_account_payable
            if account_id:
                line.account_id = account_id

    def write(self, vals):
        res = super().write(vals)
        for move in self:
            move.with_context(tracking_disable=True)._onchange_account_id()
        return res

    def _get_payment_terms_account(self):
        """
        Get the account from invoice that will be set as receivable / payable account.
        :return:                        An account.account record.
        """
        if self.partner_id:
            # Retrieve account from partner.
            if self.is_sale_document(include_receipts=True):
                return self.partner_id.property_account_receivable_id
            else:
                return self.partner_id.property_account_payable_id
        else:
            # Search new account.
            domain = [
                ('company_id', '=', self.company_id.id),
                ('account_type', '=', 'asset_receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'liability_payable'),
                ('deprecated', '=', False),
            ]
            return self.env['account.account'].search(domain, limit=1)

    def _get_data_from_account_payment_term_lines(self, term):
        res = super(AccountMove, self)._get_data_from_account_payment_term_lines(term)
        new_account = self._get_payment_terms_account()
        account_line_ids = term['term_extension']
        account_line = account_line_ids.search(
            [('currency.id', '=', self.currency_id.id), ('id', 'in', account_line_ids.ids)], limit=1)
        ledger_account_related = account_line.ledger_account
        ledger_account_payable_related = account_line.ledger_account_payable
        if ledger_account_related and self.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
            new_account = ledger_account_related
        elif ledger_account_payable_related and self.move_type in ('in_invoice', 'in_refund', 'in_receipt'):
            new_account = ledger_account_payable_related
        res['term_account_id'] = new_account.id if new_account else False
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    term_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Parametro temporal para tener calculado cuenta de la linea del término de pago'
    )

    def _set_payment_terms_account(self, payment_terms_lines):
        for line in payment_terms_lines:
            if line.term_account_id:
                line.account_id = line.term_account_id

    def _compute_account_id(self):
        super()._compute_account_id()
        term_lines = self.filtered(lambda line: line.display_type == 'payment_term')
        if term_lines:
            self._set_payment_terms_account(term_lines)