from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payment_vals_from_batch(self, batch_result):
        payment_vals = super()._create_payment_vals_from_batch(batch_result)
        
        to_force_exchange_rate = self._context.get('to_force_exchange_rate', 0.0)
        payment_vals['to_force_exchange_rate'] = to_force_exchange_rate
        
        if self.currency_id and self.currency_id != self.company_currency_id and to_force_exchange_rate != 0.0:
            payment_vals['write_off_line_vals'] = []
            
            batch_values = self._get_wizard_values_from_batch(batch_result)

            total_amount, mode = self._get_total_amount_using_same_currency(batch_result)
            currency = self.env['res.currency'].browse(batch_values['source_currency_id'])
            if mode == 'early_payment':
                payment_vals['amount'] = total_amount

                epd_aml_values_list = []
                for aml in batch_result['lines']:
                    if aml._is_eligible_for_early_payment_discount(currency, self.payment_date):
                        epd_aml_values_list.append({
                            'aml': aml,
                            'amount_currency': -aml.amount_residual_currency,
                            'balance': aml.company_currency_id.round(-aml.amount_residual_currency * to_force_exchange_rate),
                        })

                open_amount_currency = (batch_values['source_amount_currency'] - total_amount) * (-1 if batch_values['payment_type'] == 'outbound' else 1)
                open_balance = self.company_id.currency_id.round(open_amount_currency * to_force_exchange_rate)
                early_payment_values = self.env['account.move']._get_invoice_counterpart_amls_for_early_payment_discount(epd_aml_values_list, open_balance)
                for aml_values_list in early_payment_values.values():
                    payment_vals['write_off_line_vals'] += aml_values_list
        return payment_vals

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        
        to_force_exchange_rate = self._context.get('to_force_exchange_rate', 0.0)
        payment_vals['to_force_exchange_rate'] = to_force_exchange_rate
        
        if self.currency_id and self.currency_id != self.company_currency_id and to_force_exchange_rate != 0.0:
            payment_vals['write_off_line_vals'] = []

            if self.payment_difference_handling == 'reconcile':

                if self.early_payment_discount_mode:
                    epd_aml_values_list = []
                    for aml in batch_result['lines']:
                        if aml._is_eligible_for_early_payment_discount(self.currency_id, self.payment_date):
                            epd_aml_values_list.append({
                                'aml': aml,
                                'amount_currency': -aml.amount_residual_currency,
                                'balance': aml.company_currency_id.round(-aml.amount_residual_currency * to_force_exchange_rate),
                            })

                    open_amount_currency = self.payment_difference * (-1 if self.payment_type == 'outbound' else 1)
                    open_balance = self.company_id.currency_id.round(open_amount_currency * to_force_exchange_rate)
                    early_payment_values = self.env['account.move']._get_invoice_counterpart_amls_for_early_payment_discount(epd_aml_values_list, open_balance)
                    for aml_values_list in early_payment_values.values():
                        payment_vals['write_off_line_vals'] += aml_values_list

                elif not self.currency_id.is_zero(self.payment_difference):
                    if self.payment_type == 'inbound':
                        # Receive money.
                        write_off_amount_currency = self.payment_difference
                    else: # if self.payment_type == 'outbound':
                        # Send money.
                        write_off_amount_currency = -self.payment_difference

                    write_off_balance = self.company_id.currency_id.round(write_off_amount_currency * to_force_exchange_rate)
                    payment_vals['write_off_line_vals'].append({
                        'name': self.writeoff_label,
                        'account_id': self.writeoff_account_id.id,
                        'partner_id': self.partner_id.id,
                        'currency_id': self.currency_id.id,
                        'amount_currency': write_off_amount_currency,
                        'balance': write_off_balance,
                    })
        return payment_vals
