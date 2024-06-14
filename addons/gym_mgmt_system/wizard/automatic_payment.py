# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SelectPaymentModeWizard(models.TransientModel):
    _name = 'select.payment.mode.wizard'
    _description = 'Asistente de asignación de modo de pago'

    # Retorna el contrato actual
    def _default_membership(self):
        return self.env['gym.membership'].browse(self._context.get('active_id'))

    membership_id = fields.Many2one('gym.membership', string='Membresía', required=True, default=_default_membership)
    partner_id = fields.Many2one(related='membership_id.member', string='Socio', required=True)
    partner2_id = fields.Many2one('res.partner', string='Razón Social')
    order_id = fields.Many2one(related='membership_id.sale_order_id', string='Orden de Venta', required=True)
    journal_id = fields.Many2one(related='membership_id.journal_id', string='Tipo Doc.', required=True)
    currency_id = fields.Many2one(related='order_id.currency_id', string='Moneda', readonly=True)
    amount_total = fields.Float(related='membership_id.membership_fees', string='Importe a pagar', readonly=True)
    paid_amount = fields.Float(related='membership_id.paid_amount', string='Monto Pagado', readonly=True)
    amount_diff = fields.Float('Diferencia', compute='_compute_amount_diff', readonly=True)
    # reference = fields.Char(string='Número de Factura', copy=False, help="The partner reference of this invoice.", required=True)
    date_invoice = fields.Date(string='Fecha de Factura', help="Keep empty to use the current date", copy=False, required=True, default=fields.Date.context_today)
    line_ids = fields.One2many('select.payment.mode.wizard.line', 'wizard_id', string='Detalle')

    @api.depends('amount_total', 'paid_amount', 'line_ids', 'line_ids.amount')
    def _compute_amount_diff(self):
        for wiz in self:
            wiz.amount_diff = wiz.amount_total - wiz.paid_amount - sum(wiz.line_ids.mapped('amount'))

    def action_process_sale(self):
        # Validate amounts:
        self._compute_amount_diff()
        # Order validation
        if not self.order_id:
            raise UserError('Debe confirmar la membresía antes de continuar.')
        # TODO FIXME Definir si van a poser hacer pagos parciales, por el momento, debe ser completo
        if not self.line_ids and self.amount_total > 0.0:
            raise UserError('Debe definir al menos una línea de detalle para realizar los pagos.')
        # if not self.currency_id.is_zero(self.amount_diff):
        if self.amount_diff < 0.0:
            raise UserError('El monto total de las líneas debe ser igual o menor al monto pendiente de pago (%s %.2f)' % (self.currency_id.symbol, self.amount_diff))
        
        self.order_id.write({'partner_id': self.partner2_id.id})
        if self.order_id.state != 'sale':
            self.order_id.action_confirm()

        if self.order_id.invoice_status == 'invoiced':
            invoice1 = self.order_id.invoice_ids[0]
            if not self.membership_id.invoice_id:
                self.membership_id.write({'invoice_id': invoice1.id})
        else:
            invoice1 = self.order_id._create_invoices()
            invoice1.write({
                'journal_id': self.journal_id.id,
                'invoice_date': self.date_invoice,
                'invoice_date_due': self.date_invoice,
            })
            # invoice1.compute_taxes()
            self.membership_id.write({'invoice_id': invoice1.id})
            invoice1.action_post()

        lines = invoice1.line_ids
        # early_payment_values = self.env['account.move']._get_invoice_counterpart_amls_for_early_payment_discount(epd_aml_values_list, open_balance)
        for pay in self.line_ids:
            available_payment_method_lines = pay.payment_mode_id._get_available_payment_method_lines('inbound')
            payment_method_line = available_payment_method_lines[0]._origin if available_payment_method_lines else False
            label = pay.communication if pay.communication else invoice1.name
            vals = {
                'date': self.date_invoice,
                'amount': pay.amount,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'ref': label,
                'journal_id': pay.payment_mode_id.id,
                # 'currency_id': self.currency_id.id,
                'partner_id': self.partner_id.id,
                'partner_bank_id': pay.payment_mode_id.bank_account_id.id,
                # 'payment_method_line_id': payment_method_line.id,
                # 'destination_account_id': lines[0].account_id.id,
                # 'write_off_line_vals': [],
            }
            payment = self.env['account.payment'].create(vals)
            payment.action_post()
            # reconcile
            move_line_12 = payment.move_id.line_ids.filtered(lambda r: r.debit == 0.0)[0]
            invoice1.js_assign_outstanding_line(move_line_12.id)

        return {}

class SelectPaymentModeWizardLine(models.TransientModel):
    _name = 'select.payment.mode.wizard.line'
    _description = 'Asistente de asignación de modo de pago (Detalle)'
    
    wizard_id = fields.Many2one('select.payment.mode.wizard', string='Wizard', required=True, readonly=True)
    currency_id = fields.Many2one(related='wizard_id.currency_id', readonly=True)
    payment_mode_id = fields.Many2one("account.journal", string='Diario de pago', domain="[('type', 'in', ['bank','cash'])]", required=True)
    amount = fields.Float('Monto')
    communication = fields.Char(string="Referencia", store=True, readonly=False)
