from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round

from odoo import api, fields, models, Command, _


class PaymentTermLineExtension(models.Model):
    _name = "account.payment.term.line.extension"
    _description = 'Payment lines extension'

    payment_term_line_id = fields.Many2one('account.payment.term.line')
    currency = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        required=False
    )
    ledger_account = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta contable por cobrar',
        default=False,
        help="Al colocar una cuenta contable, el plazo de pago se generará en esa cuenta contable.",
        required=False,
        company_dependent=True
    )
    ledger_account_payable = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta contable por pagar',
        default=False,
        required=False,
        company_dependent=True
    )


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def _compute_terms_line_by_type(
            self, line, term_vals, sign, currency, company, date_ref, company_currency, tax_amount,
            tax_amount_currency, untaxed_amount, untaxed_amount_currency, tax_amount_left,
            tax_amount_currency_left, untaxed_amount_left, untaxed_amount_currency_left,
            total_amount, total_amount_currency
    ):
        if line.value == 'fixed':
            company_proportion = tax_amount / untaxed_amount if untaxed_amount else 1
            foreign_proportion = tax_amount_currency / untaxed_amount_currency if untaxed_amount_currency else 1

            if line.factor_round > 0.00:
                term_vals['company_amount'] = float_round(sign * company_currency.round(line.value_amount),
                                                          precision_rounding=line.factor_round)
                term_vals['foreign_amount'] = float_round(sign * currency.round(line.value_amount),
                                                          precision_rounding=line.factor_round)
                line_tax_amount = float_round(company_currency.round(line.value_amount * company_proportion) * sign,
                                              precision_rounding=line.factor_round)
                line_tax_amount_currency = float_round(currency.round(line.value_amount * foreign_proportion) * sign,
                                                       precision_rounding=line.factor_round)
            else:
                term_vals['company_amount'] = sign * company_currency.round(line.value_amount)
                term_vals['foreign_amount'] = sign * currency.round(line.value_amount)
                line_tax_amount = company_currency.round(line.value_amount * company_proportion) * sign
                line_tax_amount_currency = currency.round(line.value_amount * foreign_proportion) * sign

            line_untaxed_amount = term_vals['company_amount'] - line_tax_amount
            line_untaxed_amount_currency = term_vals['foreign_amount'] - line_tax_amount_currency
        elif line.value == 'percent':
            if line.factor_round > 0.00:
                term_vals['company_amount'] = float_round(
                    company_currency.round(total_amount * (line.value_amount / 100.0)),
                    precision_rounding=line.factor_round)
                term_vals['foreign_amount'] = float_round(
                    currency.round(total_amount_currency * (line.value_amount / 100.0)),
                    precision_rounding=line.factor_round)
                line_tax_amount = float_round(company_currency.round(tax_amount * (line.value_amount / 100.0)),
                                              precision_rounding=line.factor_round)
                line_tax_amount_currency = float_round(
                    currency.round(tax_amount_currency * (line.value_amount / 100.0)),
                    precision_rounding=line.factor_round)
            else:
                term_vals['company_amount'] = company_currency.round(total_amount * (line.value_amount / 100.0))
                term_vals['foreign_amount'] = currency.round(total_amount_currency * (line.value_amount / 100.0))
                line_tax_amount = company_currency.round(tax_amount * (line.value_amount / 100.0))
                line_tax_amount_currency = currency.round(tax_amount_currency * (line.value_amount / 100.0))

            line_untaxed_amount = term_vals['company_amount'] - line_tax_amount
            line_untaxed_amount_currency = term_vals['foreign_amount'] - line_tax_amount_currency
        else:
            line_tax_amount = line_tax_amount_currency = line_untaxed_amount = line_untaxed_amount_currency = 0.0
        tax_amount_left -= line_tax_amount
        tax_amount_currency_left -= line_tax_amount_currency
        untaxed_amount_left -= line_untaxed_amount
        untaxed_amount_currency_left -= line_untaxed_amount_currency
        if line.value == 'balance':
            if line.factor_round > 0.00:
                term_vals['company_amount'] = float_round(tax_amount_left + untaxed_amount_left,
                                                          precision_rounding=line.factor_round)
                term_vals['foreign_amount'] = float_round(tax_amount_currency_left + untaxed_amount_currency_left,
                                                          precision_rounding=line.factor_round)
            else:
                term_vals['company_amount'] = tax_amount_left + untaxed_amount_left
                term_vals['foreign_amount'] = tax_amount_currency_left + untaxed_amount_currency_left

            line_tax_amount = tax_amount_left
            line_tax_amount_currency = tax_amount_currency_left
            line_untaxed_amount = untaxed_amount_left
            line_untaxed_amount_currency = untaxed_amount_currency_left

        if line.discount_percentage:
            if company.early_pay_discount_computation in ('excluded', 'mixed'):
                term_vals['discount_balance'] = company_currency.round(
                    term_vals['company_amount'] - line_untaxed_amount * line.discount_percentage / 100.0)
                term_vals['discount_amount_currency'] = currency.round(
                    term_vals['foreign_amount'] - line_untaxed_amount_currency * line.discount_percentage / 100.0)
            else:
                term_vals['discount_balance'] = company_currency.round(
                    term_vals['company_amount'] * (1 - (line.discount_percentage / 100.0)))
                term_vals['discount_amount_currency'] = currency.round(
                    term_vals['foreign_amount'] * (1 - (line.discount_percentage / 100.0)))
            term_vals['discount_date'] = date_ref + relativedelta(days=line.discount_days)
        return tax_amount_left, tax_amount_currency_left, untaxed_amount_left, \
            untaxed_amount_currency_left, total_amount, total_amount_currency


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    def _default_term_line_ids(self):
        return [Command.create({'currency': 'balance', 'ledger_account': '', 'ledger_account_payable': ''})]

    factor_round = fields.Float(
        string="Factor de Redondeo",
        digits="Account",
        help="En este campo se colocará el factor por el cual quiere que se redondee la línea del término de plazo, "
             "si quiere que salga sin decimales, colocar 1.00.",
    )
    day_of_the_month = fields.Integer(
        string='Day of the month',
        help="Day of the month on which the invoice must come to its term. If zero or negative, "
             "this value will be ignored, and no specific day will be set. If greater than the last day of a month, "
             "this number will instead select the last day of this month."
    )
    option = fields.Selection([
        ('day_after_invoice_date', 'Day(s) after the invoice date'),
        ('after_invoice_month', 'After the invoice month'),
        ('day_following_month', 'Day(s) of the following month'),
        ('day_current_month', 'Day(s) of the current month')
    ], string='Option', default='day_after_invoice_date'
    )
    currency = fields.Many2one(
        'res.currency',
        string='Moneda',
        required=False
    )
    ledger_account = fields.Many2one(
        'account.account',
        string='Cuenta contable por cobrar',
        default=False,
        help="Al colocar una cuenta contable, el plazo de pago se generará en esa cuenta contable.",
        required=False,
        company_dependent=True
    )
    ledger_account_payable = fields.Many2one(
        'account.account',
        string='Cuenta contable por pagar',
        default=False,
        required=False,
        company_dependent=True
    )
    term_extension = fields.One2many(
        'account.payment.term.line.extension',
        string='Cuenta contables',
        inverse_name='payment_term_line_id',
        default=_default_term_line_ids,
    )

    def _get_data_from_line_ids(self, date_ref):
        res = super(AccountPaymentTermLine, self)._get_data_from_line_ids(date_ref)
        res['term_extension'] = self.term_extension
        return res

    @api.onchange('option')
    def _onchange_option(self):
        if self.option in ('day_current_month', 'day_following_month'):
            self.days = 0

    @api.constrains('days')
    def _check_days(self):
        for term_line in self:
            if term_line.option in ('day_following_month', 'day_current_month') and term_line.days <= 0:
                raise ValidationError(_("The day of the month used for this term must be strictly positive."))
            elif term_line.days < 0:
                raise ValidationError(_("The number of days used for a payment term cannot be negative."))
