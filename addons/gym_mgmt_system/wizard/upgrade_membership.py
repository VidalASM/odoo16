# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class UpgradeMembershipWizard(models.TransientModel):
    _name = 'upgrade.membership.wizard'
    _description = 'Asistente para actualizar membresia'

    # Retorna el contrato actual
    def _default_membership(self):
        return self.env['gym.membership'].browse(self._context.get('active_id'))

    def _default_partner(self):
        membership = self.env['gym.membership'].browse(self._context.get('active_id'))
        if membership.invoice_id:
            return membership.invoice_id.partner_id.id
        return False

    def _default_journal(self):
        return self.env['gym.membership'].browse(self._context.get('active_id')).journal_id.id

    membership_id = fields.Many2one('gym.membership', string='Membresía', required=True, default=_default_membership)
    partner_id = fields.Many2one('res.partner', string='Socio', default=_default_partner)
    membership_scheme = fields.Many2one('product.product', string='Membresía Nueva', required=True, tracking=4)
    membership_fees = fields.Float(string="Monto Nuevo", tracking=4, store=True)
    amount_total = fields.Float(related='membership_id.membership_fees', string='Monto Actual', readonly=True)
    amount_diff = fields.Float('Importe a Pagar', compute='_compute_amount_diff')
    journal_id = fields.Many2one('account.journal', string='Tipo Doc. Boleta', required=True, default=_default_journal, check_company=True, domain="[('type', '=', 'sale')]")
    journal_rec_id = fields.Many2one('account.journal', string='Tipo Doc. Nota Crédito', required=True, check_company=True, domain="[('type','=','sale'), ('l10n_latam_document_type_id.code','=','07')]")

    order_id = fields.Many2one(related='membership_id.sale_order_id', string='Orden de Venta', required=True)
    currency_id = fields.Many2one(related='order_id.currency_id', string='Moneda', readonly=True)
    
    # reference = fields.Char(string='Número de Factura', copy=False, help="The partner reference of this invoice.", required=True)
    date_invoice = fields.Date(string='Fecha de Factura', help="Keep empty to use the current date", copy=False, required=True, default=fields.Date.context_today)
    line_ids = fields.One2many('upgrade.membership.wizard.line', 'wizard_id', string='Detalle')

    @api.onchange('membership_scheme')
    def _onchange_membership_scheme(self):
        if self.membership_scheme:
            self.membership_fees = self.membership_scheme.lst_price

    @api.depends('membership_fees', 'amount_total', 'line_ids', 'line_ids.amount')
    def _compute_amount_diff(self):
        for wiz in self:
            wiz.amount_diff = wiz.membership_fees - wiz.amount_total - sum(wiz.line_ids.mapped('amount'))

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
                self.membership_id.write({'invoice_id': invoice1.id, 'state_contract': 'active'})
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
                'partner_id': self.partner2_id.id,
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
        self.order_id.write({'state':'sent'})

        return {}

class UpgradeMembershipWizardLine(models.TransientModel):
    _name = 'upgrade.membership.wizard.line'
    _description = 'Asistente de asignación de modo de pago (Detalle)'

    # Retorna el pago automatico actual
    def _default_amount(self):
        # return self.env['gym.membership'].browse(self._context.get('active_id')).membership_fees
        amount_diff = self.wizard_id.amount_diff
        return amount_diff
    
    wizard_id = fields.Many2one('upgrade.membership.wizard', string='Wizard', required=True, readonly=True)
    currency_id = fields.Many2one(related='wizard_id.currency_id', readonly=True)
    payment_mode_id = fields.Many2one("account.journal", string='Diario de pago', domain="[('type', 'in', ['bank','cash'])]", required=True)
    type = fields.Selection([
            ('sale', 'Sales'),
            ('purchase', 'Purchase'),
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('general', 'Miscellaneous'),
        ], related='payment_mode_id.type', string='Tipo', readonly=True)
    amount = fields.Float('Monto', default=lambda self:self.wizard_id.amount_diff)
    communication = fields.Char(string="Referencia", store=True, readonly=False)
