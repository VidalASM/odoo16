# -*- coding: utf-8 -*-
from odoo import api, fields, models

import logging
log = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_pe_edi_pse_uid = fields.Char(string='PSE Unique identifier', copy=False)
    l10n_pe_edi_pse_cancel_uid = fields.Char(string='PSE Identifier for Cancellation', copy=False)
    l10n_pe_edi_accepted_by_sunat = fields.Boolean(string='EDI Accepted by Sunat', copy=False)
    l10n_pe_edi_void_accepted_by_sunat = fields.Boolean(string='Void EDI Accepted by Sunat', copy=False)
    l10n_pe_edi_rectification_ref_type = fields.Many2one('l10n_latam.document.type', string='Rectification - Invoice Type')
    l10n_pe_edi_rectification_ref_number = fields.Char('Rectification - Invoice number')
    l10n_pe_edi_rectification_ref_date = fields.Char('Rectification - Invoice Date')
    l10n_pe_edi_payment_fee_ids = fields.One2many('account.move.l10n_pe_payment_fee','move_id', string='Credit Payment Fees')
    l10n_pe_edi_transportref_ids = fields.One2many(
        'account.move.l10n_pe_transportref', 'move_id', string='Attached Despatchs', copy=True)

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        pe_edi_format = self.env.ref('l10n_pe_edi_pse_factura.edi_pe_pse')
        for move in self.filtered(lambda m: m.l10n_pe_edi_is_required):
            move.l10n_pe_edi_compute_fees()
        return res
    
    def _get_starting_sequence(self):
        # OVERRIDE
        if self.l10n_pe_edi_is_required and self.l10n_latam_document_type_id:
            doc_mapping = {'01': 'FFI', '03': 'BOL', '07': 'CNE', '08': 'NDI'}
            middle_code = doc_mapping.get(self.l10n_latam_document_type_id.code, self.journal_id.code)
            # TODO: maybe there is a better method for finding decent 2nd journal default invoice names
            if self.journal_id.code != 'INV':
                middle_code = self.journal_id.code[:3]
            return "%s %s-00000000" % (self.l10n_latam_document_type_id.doc_code_prefix, middle_code)

        return super()._get_starting_sequence()

    def l10n_pe_edi_retention_amount(self):
        if self.partner_id.l10n_pe_edi_retention_type:
            return self.amount_total*(0.03 if self.partner_id.l10n_pe_edi_retention_type=='01' else 0.06)
        return 0

    def l10n_pe_edi_credit_amount_deduction(self):
        spot = self._l10n_pe_edi_get_spot()
        amount = 0
        if spot:
            amount+=spot['spot_amount']
        if self.partner_id.l10n_pe_edi_retention_type:
            amount+=self.l10n_pe_edi_retention_amount()
        return amount

    def l10n_pe_edi_compute_fees(self):
        self.l10n_pe_edi_payment_fee_ids.unlink()
        if self.invoice_date_due and self.invoice_date_due>self.invoice_date:
            invoice_date_due_vals_list = []
            first_time = True
            amount_deduction = self.l10n_pe_edi_credit_amount_deduction()
            for rec_line in self.line_ids.filtered(lambda l: l.account_type=='asset_receivable'):
                amount = rec_line.amount_currency
                if rec_line.date_maturity<=self.invoice_date:
                    continue
                if amount_deduction and first_time:
                    amount -= amount_deduction
                invoice_date_due_vals_list.append([0, 0,{'amount_total': rec_line.move_id.currency_id.round(amount),
                                                'currency_id': rec_line.move_id.currency_id.id,
                                                'date_due': rec_line.date_maturity}])

            self.write({
                'l10n_pe_edi_payment_fee_ids': invoice_date_due_vals_list
            })

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_pe_edi_downpayment_line = fields.Boolean('Is Downpayment?', store=True, default=False)
    l10n_pe_edi_downpayment_invoice_id = fields.Many2one('account.move', string='Downpayment Invoice', store=True, readonly=True, help='Invoices related to the advance regualization')
    l10n_pe_edi_downpayment_ref_type = fields.Selection([('02','Factura'),('03','Boleta de venta')], string='Downpayment Ref. Type')
    l10n_pe_edi_downpayment_ref_number = fields.Char('Downpayment Ref. Number')
    l10n_pe_edi_downpayment_date = fields.Date('Downpayment date')

    def _prepare_edi_vals_to_export(self):
        res = super()._prepare_edi_vals_to_export()
        res.update({
            'price_subtotal_unit': self.price_subtotal / self.quantity if self.quantity else 0.0,
            'price_total_unit': self.price_total / self.quantity if self.quantity else 0.0,
        })
        return res