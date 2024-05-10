# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Shahul Faiz (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models, _, Command
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning(
        "The num2words python library is not installed, amount-to-text features won't "
        "be fully available."
    )
    num2words = None

PAYMENT_STATUS = [
    ('not_paid', 'Not Paid'),
    ('paid', 'Paid'),
    ('partial', 'Partially Paid'),
    ('reversed', 'Reversed'),
]    

class GymMembership(models.Model):
    _name = "gym.membership"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Gym Membership"
    _rec_name = "reference"

    reference = fields.Char(string='Referencia', required=True, readonly=True, default=lambda self: _('New'))
    member = fields.Many2one('res.partner', string='Socio', required=True, tracking=4, domain="[('gym_member', '!=',False)]")
    age = fields.Integer("Edad", related="member.age", store=True)
    gender = fields.Selection("Género", related="member.gender", store=True)
    membership_scheme = fields.Many2one('product.product', string='Producto', required=True, tracking=4)
    paid_amount = fields.Float(string="Monto pagado", tracking=4, compute="_compute_amount")
    membership_fees = fields.Float(string="Precio", tracking=4, related="membership_scheme.list_price", store=True)
    sale_order_id = fields.Many2one('sale.order', string='Orden de venta', ondelete='cascade', copy=False, readonly=False)
    # sale_order_ids = fields.One2many(
    #     'sale.order', 'membership_id', 'Ordenes de venta')
    invoice_id = fields.Many2one('account.move', string='Factura', ondelete='cascade', copy=False, readonly=False)
    # invoice_pay_status = fields.Selection(
    #     selection=INVOICE_STATUS,
    #     string="Invoice Status",
    #     compute='_compute_invoice_status',
    #     store=True)
    membership_date_from = fields.Date(string='Fecha de inicio de la membresía', tracking=5, default=datetime.today(), 
        help='Date from which membership becomes active.')
    membership_date_to = fields.Date(string='Fecha de vencimiento de la membresía', tracking=5, compute="_compute_membership_date_to", 
        help='Date until which membership remains active.', store=True)
    journal_id = fields.Many2one(
        'account.journal',
        string='Tipo Doc.',
        store=True, readonly=False,
        required=True, tracking=4,
        states={'draft': [('readonly', False)]},
        check_company=True,
        domain="[('type', '=', 'sale')]",
    )
    adendum = fields.Text("Adendum")
    restrictions = fields.Html("Restricciones", related="membership_scheme.description")
    state_contract = fields.Selection(string='Estado de Contrato', 
        selection=[('active', 'Activo'), ('inactive', 'Inactivo'), ('freezing', 'Freezing'),('pending', 'Pendiente'),],
        tracking=3, default='pending')
    freeze_ids = fields.One2many(comodel_name='membership.freeze', inverse_name='contract_id', string='Freezers', ondelete='cascade')
    transfer_ids = fields.One2many(comodel_name='membership.transfer', inverse_name='contract_id', string='Transeferencias')
    company_id = fields.Many2one('res.company', string='Sede', required=True, readonly=False,
        default=lambda self: self.env.company)
    opportunity_id = fields.Many2one(
        'crm.lead', string='Oportunidad', check_company=True,
        domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    #Si este contratro fue transferido entonces modificara la fecha de inicio.
    days_transferred = fields.Integer()
    
    # Discount autorization
    discount = fields.Float(
        string="Descuento (%)",
        digits='Discount',
        store=True
    )
    authorize_user = fields.Many2one(comodel_name='res.users', string="Autoriza", 
                                     states={'draft': [('readonly', False)], 'confirm': [('readonly', True)]}, ondelete='cascade')
    addendum = fields.Char(string='Adenda', required=False)
    # Anexo 3
    sign_request_ids = fields.One2many(comodel_name='sign.request', inverse_name='membership', string='Anexos')

    _sql_constraints = [
        ('membership_date_greater',
         'check(membership_date_to >= membership_date_from)',
         'Error ! Ending Date cannot be set before Beginning Date.')
    ]
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=2, string='Status')
    type_contract = fields.Selection([('1', 'Nuevo'), ('2', 'Renovación'),('3','Traspaso'),('4','Invitado'),('5','Referido')], string="Tipo de Contrato")

    @api.depends('invoice_id.amount_total', 'invoice_id.amount_residual')
    def _compute_amount(self):
        """ to get the total of paids """
        for rec in self:
            if rec.invoice_id:
                rec.paid_amount = rec.invoice_id.amount_total - rec.invoice_id.amount_residual
            else:
                rec.paid_amount = 0.0

    @api.depends('membership_scheme', 'membership_date_from', 'freeze_ids')
    def _compute_membership_date_to(self):
        """ to get membership_date_to """
        for rec in self:
            res = rec.membership_date_from
            templ = rec.membership_scheme.product_tmpl_id
            date = fields.Date.from_string(rec.membership_date_from)
            if rec.type_contract == '3':
                res = date + timedelta(days=rec.days_transferred)
            elif templ.membership_type == "variable":
                delta = templ.membership_interval_qty
                if templ.membership_interval_unit == "days":
                    res = date + timedelta(days=delta)
                elif templ.membership_interval_unit == "weeks":
                    res = date + timedelta(weeks=delta)
                elif templ.membership_interval_unit == "months":
                    res = date + relativedelta(months=delta)
                elif templ.membership_interval_unit == "years":
                    res = date + relativedelta(years=delta)
            
            contract_days_freeze = sum(rec.freeze_ids.mapped('quantity_days')) if rec.freeze_ids else 0
            res += timedelta(days=contract_days_freeze)
                
            # date_to = rec.membership_scheme._get_next_date(rec.membership_date_from, qty=1)
            rec.membership_date_to = res

    @api.model
    def create(self, vals):
        """ sequence number for membership """
        if vals.get('reference', ('New')) == ('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'gym.membership') or ('New')
        res = super(GymMembership, self).create(vals)
        return res
    
    def open_sale_order(self):
        self.ensure_one()
        order_id = self.sale_order_id
        if order_id and order_id.state == 'draft':
            order_id.action_quotation_sent()
        order_id.write({'state': 'sent'})
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': order_id.get_portal_url(),
        }
    
    def create_membership_invoice(self):
        invoice_list = self.member.create_membership_invoice(self.membership_scheme, self.membership_fees)

        search_view_ref = self.env.ref('account.view_account_invoice_filter', False)
        form_view_ref = self.env.ref('account.view_move_form', False)
        tree_view_ref = self.env.ref('account.view_move_tree', False)

        return  {
            'domain': [('id', 'in', invoice_list.ids)],
            'name': 'Membership Invoices',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
            'search_view_id': search_view_ref and [search_view_ref.id],
        }
    
    def create_membership_sale(self):
        if self.state == 'draft' and not self.sale_order_id:
            sale_order = self.env['sale.order'].create({
                'partner_id': self.member.id,
                'is_contract': True,
            })
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'name': self.membership_scheme.name,
                'product_id': self.membership_scheme.id,
                'price_unit': self.membership_fees,
                'product_uom_qty': 1,
            })
            self.sale_order_id = sale_order.id
            self.state = 'confirm'

    def _get_amount_in_words(self):
        """Transform the amount to text"""
        if num2words is None:
            logging.getLogger(__name__).warning(
                "The library 'num2words' is missing, cannot render textual amounts."
            )
            return ""
        amount_base = self.membership_scheme.membership_interval_qty

        lang_code = self.env.context.get("lang") or self.env.user.lang
        lang = self.env["res.lang"].search([("code", "=", lang_code)])
        words = num2words(amount_base, lang=lang.iso_code)
        return words.upper()
    
    # Enviar contrato de apoderado
    def send_parent_signature(self):
        self.ensure_one()
        # request = self.env['sign.send.request']
        sign_request = self.env['sign.send.request'].create({
            'set_sign_order': False, 
            'template_id': 12, 
            'signer_ids': [[0, 'virtual_3', {'role_id': 1, 'partner_id': self.member.tutor_id.id, 'mail_sent_order': 1}]], 
            'signer_id': False, 
            'signers_count': 1, 
            'has_default_template': True, 
            'subject': 'Solicitud de firma - ANEXO 3.pdf (v3)', 
            'filename': 'ANEXO 3.pdf (v3)', 
            'cc_partner_ids': [[6, False, []]], 
            'message_cc': False, 
            'attachment_ids': [[6, False, []]], 
            'message': False, 
            'refusal_allowed': False, 
            'membership': self.id

            # 'template_id': 12,
            # 'filename': 'Petición de firma',
            # 'subject': 'Solicitud de firma - ANEXO 3.pdf (v3)',
            # 'message': '',
            # 'message_cc': '',
            # 'signer_id': self.member.tutor_id.id,
        })
        # self.env['sign.send.request.signer'].create({
        #     'role_id': 4,
        #     'partner_id': self.member.tutor_id.id,
        #     'sign_send_request_id': sign_request.id,
        # })
        sign_request.send_request()

    def print_invoice(self):
        """ to override for each type of models that will use this composer."""
        self.ensure_one()
        return self.env.ref('l10n_pe_edi_odoofact.invoice_ticket_80').report_action(self.invoice_id)


class SaleConfirm(models.Model):
    _inherit = "sale.order"

    # membership_id = fields.Many2one('gym.membership', 'Membresía', ondelete='cascade', index=True)
    is_contract = fields.Boolean(string="Es membresìa", default=False)
    membership_ids = fields.One2many(
        'gym.membership', 'sale_order_id', 'Membresías')

    def action_confirm(self):
        """ membership  created directly from sale order confirmed """
        res = super(SaleConfirm, self).action_confirm()

        # product = self.env['product.product'].search([
        #     ('membership_date_from', '!=', False),
        #     ('id', '=', self.order_line.product_id.id)])
        # for record in product:
        #     self.env['gym.membership'].create([
        #         {'member': self.partner_id.id,
        #          'membership_date_from': record.membership_date_from,
        #          'membership_scheme': self.order_line.product_id.id,
        #          'sale_order_id': self.id,
        #          }])
            
        return res

class MembershipFreeze(models.Model):
    _name = "membership.freeze"

    number_freeze = fields.Char(string='Nro de Solicitud')
    cause = fields.Char(string='Motivo del freeze')
    date_freeze = fields.Date(string='Fecha registrada')
    start_date = fields.Date(string='Desde')
    end_date = fields.Date(string='Reinicio')
    quantity_days = fields.Integer(string='Valor en días')
    contract_id = fields.Many2one(comodel_name='gym.membership', string='Contrato',ondelete='cascade')
    counter_id = fields.Many2one(comodel_name='res.users', string="Por", ondelete='cascade')
    is_force = fields.Selection(string='Forzado', selection=[('si', 'Si'), ('no', 'No')], default='no')
    state_freeze = fields.Boolean(string='Estado', default=False)
    sede_id = fields.Many2one(string='Sede', related='contract_id.company_id')

class MembershipTransfer(models.Model):
    _name = "membership.transfer"

    number_transfer = fields.Char(string='Nro de Solicitud')
    client_id = fields.Many2one('res.partner', string='Socio a transferir',ondelete='cascade')
    client2_id = fields.Many2one('res.partner', string='Socio emisor',ondelete='cascade')
    contract_id = fields.Many2one('gym.membership', string='Contrato origen',ondelete='cascade')
    contract2_id = fields.Many2one(comodel_name='gym.membership', string='Contrato destino',ondelete='cascade')
    reason_transfer = fields.Char(string='Motivo de la transferencia')
    date_transfer = fields.Date(string='Fecha de la transferencia')
    days_transferred = fields.Integer(string='Días transferidos')
    currente_transfer = fields.Date(string='Vigente desde')