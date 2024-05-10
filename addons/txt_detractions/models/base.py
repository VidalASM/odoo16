import base64

from odoo.exceptions import UserError

from odoo import api, fields, models
from ..reports.report_detractions import ReportInvBalTxt


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    reference_invoice = fields.Many2one(
        string='Factura Referencia',
        comodel_name='account.move',
        domain="[('partner_id', '=', partner_id), ('payment_state', 'in', ('paid', 'partial', 'in_payment'))]"
    )
    detractions_constancy_number = fields.Char(string='Número de constancia')
    filter_detraction = fields.Boolean(compute='_compute_filter_detraction')
    payment_method_name = fields.Char(compute='_compute_filter_detraction')

    tempora_accmov = fields.Many2many('account.move', string="Temporal Account Move", store=True)

    @api.depends('payment_method_line_id', 'journal_id')
    def _compute_filter_detraction(self):
        for rec in self:
            if rec.payment_method_line_id.name in ['Detracción', 'Autodetracción'] and rec.journal_id.type == 'bank':
                rec.filter_detraction = True
            else:
                rec.filter_detraction = False

    def calculate_detractions(self):
        account_move = self.reference_invoice
        discount_percentage = False
        # We look for if there is a l10n_pe_withhold_percentage not false
        for lines in account_move.invoice_line_ids:
            if lines.product_id.l10n_pe_withhold_percentage:
                discount_percentage = lines.product_id.l10n_pe_withhold_percentage
                break

        if not discount_percentage:
            return
        else:
            if account_move.currency_id and account_move.currency_id.name == 'PEN':
                self.amount = round(account_move.amount_total * (discount_percentage / 100))
            else:
                self.amount = account_move.amount_total * (discount_percentage / 100)
            self.currency_id = account_move.currency_id

        account_not_found = True
        for line in account_move.line_ids:
            if line.l10n_pe_is_detraction_retention:
                self.destination_account_id = line.account_id
                account_not_found = False
                break
        if account_not_found:
            self.destination_account_id = self.partner_id.property_account_receivable_id.id

    @api.onchange('detractions_constancy_number')
    def update_account_move_from_account_payment(self):
        if self.batch_payment_id and (
                self.batch_payment_id.state == 'reconciled' or self.batch_payment_id.state == 'sent') and self.payment_method_name == 'Detracción':
            self.env['account.move'].search([('name', '=', self.tempora_accmov.name)]).update(
                {'voucher_number': self.detractions_constancy_number,
                 'voucher_payment_date': self.batch_payment_id.date})
        if self.batch_payment_id and (
                self.batch_payment_id.state == 'reconciled' or self.batch_payment_id.state == 'sent') and self.payment_method_name == 'Autodetracción':
            self.env['account.move'].search([('name', '=', self.reference_invoice.name)]).update(
                {'voucher_number': self.detractions_constancy_number,
                 'voucher_payment_date': self.batch_payment_id.date})


class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'

    lot_number = fields.Char(string='Número de lote')
    payment_method_line_detraction = fields.Many2one(
        comodel_name='account.payment.method.line',
        string='Método para pago masivo',
        compute='_compute_filter_detraction'
    )
    payment_method_name = fields.Char(
        name='Payment method name',
        compute='_compute_filter_detraction'
    )
    txt_filename = fields.Char(string='Filaname .txt')
    txt_binary = fields.Binary(string='Reporte .TXT')
    payment_ids = fields.One2many(readonly=False)

    @api.depends('payment_ids')
    def _compute_filter_detraction(self):
        for rec in self:
            payment_method_line_detraction = False
            if rec.payment_ids:
                for payment in rec.payment_ids:
                    if payment.payment_method_line_id:
                        payment_method_line_detraction = payment.payment_method_line_id
            rec.payment_method_line_detraction = payment_method_line_detraction
            rec.payment_method_name = payment_method_line_detraction and payment_method_line_detraction.name

    # @override
    @api.depends('currency_id', 'payment_ids.amount')
    def _compute_from_payment_ids(self):
        for batch in self:
            amount_residual = 0.0
            for payment in batch.payment_ids:
                liquidity_lines, _counterpart_lines, _writeoff_lines = payment._seek_for_lines()
                for line in liquidity_lines:
                    amount_residual += line.amount_residual

            batch.amount_residual = amount_residual
            batch.amount = amount_residual
            batch.amount_residual_currency = amount_residual

    def generate_detraction(self):
        amount_total = 0
        withhold_code = '000'
        for payment in self.payment_ids:
            if payment.reconciled_bill_ids:
                for line in payment.reconciled_bill_ids.invoice_line_ids:
                    if line.product_id.l10n_pe_withhold_code:
                        withhold_code = line.product_id.l10n_pe_withhold_code
            elif payment.reference_invoice:
                for line in payment.reference_invoice.invoice_line_ids:
                    if line.product_id.l10n_pe_withhold_code:
                        withhold_code = line.product_id.l10n_pe_withhold_code
            if payment.currency_id.name == 'PEN':
                amount_total = amount_total + payment.amount
            else:
                amount_not_PEN_total = 0
                for acc_move in payment.move_id.line_ids:
                    amount_not_PEN_total = acc_move.credit or acc_move.debit
                amount_total = amount_total + round(amount_not_PEN_total)
        amount_total = str(round(amount_total)) + '.00'

        if self.payment_method_name == 'Detracción':
            bank_nation = False
            line_data = {
                '01': '*',
                'ruc': self.env.company.vat,
                'name': self.env.company.name,
                'lot_number': self.lot_number,
                'total_amount': amount_total
            }

            list_data = []
            for obj_line in self.payment_ids:
                obj_line.tempora_accmov = obj_line.reconciled_bill_ids
                for bank in obj_line.partner_id.bank_ids:
                    if bank.bank_id.bic == 'BANCPEPL':
                        bank_nation = (bank.acc_number).replace('-', '')

                if obj_line.currency_id.name == 'PEN':
                    values = {
                        'ruc': obj_line.partner_id.vat,
                        'selection_ids': withhold_code,
                        'bank': bank_nation,
                        'amount': str(obj_line.amount),
                        'operation_type': obj_line.reconciled_bill_ids.operation_type_detraction,
                        'invoice_date': obj_line.reconciled_bill_ids.invoice_date,
                        'document_type': obj_line.reconciled_bill_ids.l10n_latam_document_type_id.code,
                        'ref': obj_line.reconciled_bill_ids.ref
                    }
                    list_data.append(values)
                else:
                    for acc_mov in obj_line.move_id.line_ids:
                        if acc_mov.account_id.account_type == 'asset_current':
                            amount_not_PEN = acc_mov.credit or acc_mov.debit
                            amount_not_PEN = round(amount_not_PEN)
                    values = {
                        'ruc': obj_line.partner_id.vat,
                        'selection_ids': withhold_code,
                        'bank': bank_nation,
                        'amount': str(amount_not_PEN) + '.00',
                        'operation_type': obj_line.reconciled_bill_ids.operation_type_detraction,
                        'invoice_date': obj_line.reconciled_bill_ids.invoice_date,
                        'document_type': obj_line.reconciled_bill_ids.l10n_latam_document_type_id.code,
                        'ref': obj_line.reconciled_bill_ids.ref
                    }
                    list_data.append(values)
        elif self.payment_method_name == 'Autodetracción':
            for bank in self.env.company.partner_id.bank_ids:
                if bank.bank_id.bic == 'BANCPEPL':
                    bank_nation = (bank.acc_number).replace('-', '')
            line_data = {
                '01': 'P',
                'ruc': self.env.company.vat,
                'name': self.env.company.name,
                'lot_number': self.lot_number,
                'total_amount': amount_total
            }
            list_data = []
            for obj_line in self.payment_ids:
                if not obj_line.reference_invoice:
                    raise UserError("Usted debe seleccionar una factura de referencia para que pueda generar su txt."
                                    "Deberá ir al módulo de pagos y seleccionar su factura de referencia")
                else:
                    if obj_line.currency_id.name == 'PEN':
                        values = {
                            'ruc': obj_line.partner_id.vat,
                            'selection_ids': withhold_code,
                            'bank': bank_nation,
                            'amount': str(obj_line.amount),
                            'operation_type': obj_line.reference_invoice.operation_type_detraction,
                            'invoice_date': obj_line.reference_invoice.invoice_date,
                            'document_type': obj_line.reference_invoice.l10n_latam_document_type_id.code,
                            'ref': obj_line.reference_invoice.name.replace(' ', '')
                        }
                        list_data.append(values)
                    else:
                        for acc_mov in obj_line.move_id.line_ids:
                            if acc_mov.account_id.account_type == 'asset_current':
                                amount_not_PEN = acc_mov.credit or acc_mov.debit
                                amount_not_PEN = round(amount_not_PEN)
                        values = {
                            'ruc': obj_line.partner_id.vat,
                            'selection_ids': withhold_code,
                            'bank': bank_nation,
                            'amount': str(amount_not_PEN) + '.00',
                            'operation_type': obj_line.reference_invoice.operation_type_detraction,
                            'invoice_date': obj_line.reference_invoice.invoice_date,
                            'document_type': obj_line.reference_invoice.l10n_latam_document_type_id.code,
                            'ref': obj_line.reference_invoice.name.replace(' ', '')
                        }
                        list_data.append(values)

        else:
            return

        data_name = {
            'vat': self.env.company.vat,
            'lot_number': self.lot_number
        }
        report_txt = ReportInvBalTxt(data_name, line_data, list_data)

        values_content = report_txt.get_content()

        data = {
            'txt_binary': base64.b64encode(values_content.encode() or '\n'.encode()),
            'txt_filename': report_txt.get_filename(),
        }
        self.write(data)
        return


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    filter_detraction = fields.Boolean(compute='_compute_filter_detraction')

    @api.depends('payment_method_line_id', 'journal_id')
    def _compute_filter_detraction(self):
        for rec in self:
            if rec.payment_method_line_id.name in ['Detracción', 'Autodetracción'] and rec.journal_id.type == 'bank':
                rec.filter_detraction = True
            else:
                rec.filter_detraction = False

    def calculate_detraction_register(self):
        self.ensure_one()
        line = self.line_ids._origin
        account_move = line.move_id
        discount_percentage = False
        for lines in account_move.invoice_line_ids:
            if lines.product_id.l10n_pe_withhold_percentage:
                discount_percentage = lines.product_id.l10n_pe_withhold_percentage
                break
        if not discount_percentage:
            return
        else:
            self.currency_id = account_move.currency_id
            if account_move.currency_id.name == 'PEN':
                self.amount = round(account_move.amount_total * (discount_percentage / 100))
            else:
                self.amount = account_move.amount_total * (discount_percentage / 100)
            return {
                'name': 'Register Payment',
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.payment.register',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
