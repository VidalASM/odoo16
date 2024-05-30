from dateutil.relativedelta import relativedelta
from odoo.tools import format_date, frozendict

from odoo import api, fields, models


class AccountAccountType(models.Model):
    _inherit = "account.account"

    related_user_account_name = fields.Selection(
        name='Related user account name',
        related='account_type'
    )


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    l10n_pe_is_detraction_retention = fields.Boolean(string='¿Es un descuento?')

    def _get_data_from_line_ids(self, date_ref):
        term_date = self._get_due_date(date_ref)
        tmp_date_maturity = term_date
        if self.value == 'balance' and self.months == 0 and self.days == 0:
            # Se fuerza el cambio de fecha por un dia inferior para evitar agrupar cuando es de tipo Saldo y no hay diferencia de dias
            tmp_date_maturity += relativedelta(days=-1)
        return {
            'date': term_date,
            'tmp_date_maturity': tmp_date_maturity,
            'l10n_pe_is_detraction_retention': self.l10n_pe_is_detraction_retention,
            'has_discount': self.discount_percentage,
            'discount_date': None,
            'discount_amount_currency': 0.0,
            'discount_balance': 0.0,
            'discount_percentage': self.discount_percentage
        }


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def _compute_terms_line_by_type(
            self, line, term_vals, sign, currency, company, date_ref, company_currency, tax_amount,
            tax_amount_currency, untaxed_amount, untaxed_amount_currency, tax_amount_left,
            tax_amount_currency_left, untaxed_amount_left, untaxed_amount_currency_left,
            total_amount, total_amount_currency
    ):
        if line.value == 'fixed':
            term_vals['company_amount'] = sign * company_currency.round(line.value_amount)
            term_vals['foreign_amount'] = sign * currency.round(line.value_amount)
            company_proportion = tax_amount / untaxed_amount if untaxed_amount else 1
            foreign_proportion = tax_amount_currency / untaxed_amount_currency if untaxed_amount_currency else 1
            line_tax_amount = company_currency.round(line.value_amount * company_proportion) * sign
            line_tax_amount_currency = currency.round(line.value_amount * foreign_proportion) * sign
            line_untaxed_amount = term_vals['company_amount'] - line_tax_amount
            line_untaxed_amount_currency = term_vals['foreign_amount'] - line_tax_amount_currency
        elif line.value == 'percent':
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
        return tax_amount_left, tax_amount_currency_left, untaxed_amount_left, untaxed_amount_currency_left, \
            total_amount, total_amount_currency

    def _compute_terms(self, date_ref, currency, company, tax_amount, tax_amount_currency, sign, untaxed_amount,
                       untaxed_amount_currency):
        """
            Complete overwrite of compute method for adding method _get_data_from_line_ids.
        """
        self.ensure_one()
        company_currency = company.currency_id
        tax_amount_left = tax_amount
        tax_amount_currency_left = tax_amount_currency
        untaxed_amount_left = untaxed_amount
        untaxed_amount_currency_left = untaxed_amount_currency
        total_amount = tax_amount + untaxed_amount
        total_amount_currency = tax_amount_currency + untaxed_amount_currency
        result = []

        for line in self.line_ids.sorted(lambda x: x.value == 'balance'):
            term_vals = line._get_data_from_line_ids(date_ref)
            tax_amount_left, tax_amount_currency_left, untaxed_amount_left, untaxed_amount_currency_left, total_amount, total_amount_currency = self._compute_terms_line_by_type(
                line, term_vals, sign, currency, company, date_ref, company_currency, tax_amount,
                tax_amount_currency, untaxed_amount, untaxed_amount_currency, tax_amount_left,
                tax_amount_currency_left, untaxed_amount_left, untaxed_amount_currency_left,
                total_amount, total_amount_currency
            )
            result.append(term_vals)
        return result

    @api.model
    def _get_amount_by_date(self, terms, currency):
        """
            Se sobreescribe para que divida en lineas diferentes y no agrupe por fecha en el ejemplo visual en las lineas de pago
        """
        terms = sorted(terms, key=lambda t: t.get('date'))
        amount_by_date = {}
        for term in terms:
            key = frozendict({
                'date': term['date'],
                'discount_date': term['discount_date'],
                'discount_percentage': term['discount_percentage'],
                # Parametro para evitar que se agrupe
                'tmp_date_maturity': term['tmp_date_maturity'],
            })
            results = amount_by_date.setdefault(key, {
                'tmp_date_maturity': format_date(self.env, term['tmp_date_maturity']),
                'date': format_date(self.env, term['date']),
                'amount': 0.0,
                'discounted_amount': 0.0,
                'discount_date': format_date(self.env, term['discount_date']),
            })
            results['amount'] += term['foreign_amount']
            results['discounted_amount'] += term['discount_amount_currency']
        return amount_by_date


class AccountMove(models.Model):
    _inherit = 'account.move'

    @staticmethod
    def _get_data_from_account_payment_term_lines(term):
        return {
            'balance': term['company_amount'],
            'amount_currency': term['foreign_amount'],
            'l10n_pe_is_detraction_retention': term['l10n_pe_is_detraction_retention'],
            'discount_amount_currency': term['discount_amount_currency'] or 0.0,
            'discount_balance': term['discount_balance'] or 0.0,
            'discount_date': term['discount_date'],
            'discount_percentage': term['discount_percentage']
        }

    @api.depends('invoice_payment_term_id', 'invoice_date', 'currency_id', 'amount_total_in_currency_signed',
                 'invoice_date_due')
    def _compute_needed_terms(self):
        for invoice in self:
            is_draft = invoice.id != invoice._origin.id
            invoice.needed_terms = {}
            invoice.needed_terms_dirty = True
            sign = 1 if invoice.is_inbound(include_receipts=True) else -1
            if invoice.is_invoice(True) and invoice.invoice_line_ids:
                if invoice.invoice_payment_term_id:
                    if is_draft:
                        tax_amount_currency = 0.0
                        untaxed_amount_currency = 0.0
                        for line in invoice.invoice_line_ids:
                            untaxed_amount_currency += line.price_subtotal
                            for tax_result in (line.compute_all_tax or {}).values():
                                tax_amount_currency += -sign * tax_result.get('amount_currency', 0.0)
                        untaxed_amount = untaxed_amount_currency
                        tax_amount = tax_amount_currency
                    else:
                        tax_amount_currency = invoice.amount_tax * sign
                        tax_amount = invoice.amount_tax_signed
                        untaxed_amount_currency = invoice.amount_untaxed * sign
                        untaxed_amount = invoice.amount_untaxed_signed
                    invoice_payment_terms = invoice.invoice_payment_term_id._compute_terms(
                        date_ref=invoice.invoice_date or invoice.date or fields.Date.today(),
                        currency=invoice.currency_id,
                        tax_amount_currency=tax_amount_currency,
                        tax_amount=tax_amount,
                        untaxed_amount_currency=untaxed_amount_currency,
                        untaxed_amount=untaxed_amount,
                        company=invoice.company_id,
                        sign=sign
                    )
                    for term in invoice_payment_terms:
                        
                        key = frozendict({
                            'move_id': invoice.id,
                            'date_maturity': fields.Date.to_date(term.get('date')),
                            'discount_date': term.get('discount_date'),
                            'discount_percentage': term.get('discount_percentage'),
                            # Campo que permite evitar la agrupacion por fecha en los terminos de pago cuando calcula
                            'tmp_date_maturity': fields.Date.to_date(term.get('tmp_date_maturity')),
                        })
                        values = invoice._get_data_from_account_payment_term_lines(term)
                        if key not in invoice.needed_terms:
                            invoice.needed_terms[key] = values
                        else:
                            invoice.needed_terms[key]['balance'] += values['balance']
                            invoice.needed_terms[key]['amount_currency'] += values['amount_currency']
                else:
                    invoice.needed_terms[frozendict({
                        'move_id': invoice.id,
                        'date_maturity': fields.Date.to_date(invoice.invoice_date_due),
                        'discount_date': False,
                        'discount_percentage': 0,
                        # Campo que permite evitar la agrupacion por fecha en los terminos de pago cuando calcula por defecto
                        'tmp_date_maturity': fields.Date.to_date(invoice.invoice_date_due)
                    })] = {
                        'balance': invoice.amount_total_signed,
                        'amount_currency': invoice.amount_total_in_currency_signed,
                    }


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tmp_date_maturity = fields.Date(string='Parametro temporal para evitar que agrupe lineas de pagos por fecha')
    l10n_pe_is_detraction_retention = fields.Boolean(string='¿Es un descuento?')

    @api.depends('date_maturity', 'tmp_date_maturity')
    def _compute_term_key(self):
        for line in self:
            if line.display_type == 'payment_term':
                line.term_key = frozendict({
                    'move_id': line.move_id.id,
                    'date_maturity': fields.Date.to_date(line.date_maturity),
                    'discount_date': line.discount_date,
                    'discount_percentage': line.discount_percentage,
                    # Campo que permite evitar la agrupacion por fecha en los terminos de pago cuando se recalcula
                    'tmp_date_maturity': fields.Date.to_date(line.tmp_date_maturity)
                })
            else:
                line.term_key = False
    