
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
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import calendar
import odoorpc
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

PAYMENT_STATE_SELECTION = [
    ('not_paid', 'Not Paid'),
    ('in_payment', 'In Payment'),
    ('paid', 'Paid'),
    ('partial', 'Partially Paid'),
    ('reversed', 'Reversed'),
    ('invoicing_legacy', 'Invoicing App Legacy'),
]

class GymMembership(models.Model):
    _name = "gym.membership"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Gym Membership"
    _rec_name = "reference"

    # Retorna el responsable actual
    def _default_responsible(self):
        user_id = self.env['hr.department'].search([('company_id','=',self.env.company.id), ('parent_id','=',False)], limit=1).manager_id.user_id
        if not user_id:
            raise ValidationError("La sede actual no tiene responsable. Por favor configurar el responsable de la sede.")
        return user_id.id
    
    reference = fields.Char(string='Referencia', required=True, readonly=True, default=lambda self: _('New'))
    member = fields.Many2one('res.partner', string='Socio', required=True, tracking=4, 
        change_default=True, index=True, domain="[('gym_member', '!=',False)]")
    referred_partner_id = fields.Many2one('res.partner', string=u'Referido por')
    user_id = fields.Many2one(string='Vendedor', comodel_name='res.users', copy=False, tracking=True, default=lambda self: self.env.user,)
    responsible_id = fields.Many2one(string='Responsable', comodel_name='res.users', copy=False, tracking=True, default=_default_responsible)
    vat = fields.Char("DNI", related="member.vat", store=True)
    age = fields.Integer("Edad", related="member.age", store=True)
    gender = fields.Selection("Género", related="member.gender", store=True)
    membership_scheme = fields.Many2one('product.product', string='Producto', required=True, tracking=4)
    paid_amount = fields.Float(string="Monto pagado", tracking=4, compute="_compute_amount")
    membership_fees = fields.Float(string="Precio", tracking=4, store=True)
    sale_order_id = fields.Many2one('sale.order', string='Orden de venta', ondelete='cascade', copy=False, readonly=False)
    # sale_order_ids = fields.One2many(
    #     'sale.order', 'membership_id', 'Ordenes de venta')
    invoice_id = fields.Many2one('account.move', string='Factura', ondelete='cascade', copy=False, readonly=False)
    payment_state = fields.Selection(selection=PAYMENT_STATE_SELECTION, string="DNI", related="invoice_id.payment_state", store=True)
    # invoice_pay_status = fields.Selection(
    #     selection=INVOICE_STATUS,
    #     string="Invoice Status",
    #     compute='_compute_invoice_status',
    #     store=True)
    membership_date_from = fields.Date(string='Fecha de inicio de la membresía', tracking=5, default=fields.Date.context_today, 
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
    adendum = fields.Text("Adendum", default="- Acepto Terminos y Condiciones Y politicas de Proteccion de Datos Personales.\n- Autorizo el Tratamiento de mis datos personales para prospeccion y promocion comercial por parte de REVO SPORT.")
    restrictions = fields.Html("Restricciones", related="membership_scheme.description")
    state_contract = fields.Selection(string='Estado de Contrato', 
        selection=[('active', 'Activo'), ('inactive', 'Inactivo'), ('freezing', 'Freezing'),('pending', 'Pendiente'),],
        tracking=3, default='pending')
    freeze_ids = fields.One2many(comodel_name='membership.freeze', inverse_name='contract_id', string='Freezers', ondelete='cascade')
    transfer_ids = fields.One2many(comodel_name='membership.transfer', inverse_name='contract_id', string='Transeferencias')
    extra_days_ids = fields.One2many(comodel_name='membership.extra.days', inverse_name='contract_id', string='Días Adicionales', ondelete='cascade')
    
    company_id = fields.Many2one('res.company', string='Sede', required=True, readonly=False, default=lambda self: self.env.company)
    opportunity_id = fields.Many2one('crm.lead', string='Oportunidad', check_company=True, domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    #Si este contratro fue transferido entonces modificara la fecha de inicio.
    days_transferred = fields.Integer(string='Días Transferidos')
    
    # Discount autorization
    discount = fields.Float(
        string="Descuento (%)",
        digits='Discount',
        store=True, copy=False
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
        ('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
        ('cancelled', 'Anulado')
    ], default='draft', tracking=2, string='Status')
    type_contract = fields.Selection([('1', 'Nuevo'), ('2', 'Renovación'),('3','Traspaso'),('4','Invitado'),('5','Referido')], string="Tipo de Contrato")
    # Asistencias
    attendance_ids = fields.One2many(comodel_name='attendace.record', inverse_name='contract_id', string='Asistencia', ondelete='cascade')
    is_send = fields.Boolean(string="Sincronizado", default=False)

    @api.onchange('membership_scheme')
    def _onchange_membership_scheme(self):
        if self.membership_scheme:
            self.membership_fees = self.membership_scheme.lst_price
        
    @api.depends('invoice_id.amount_total', 'invoice_id.amount_residual')
    def _compute_amount(self):
        """ to get the total of paids """
        for rec in self:
            if rec.invoice_id:
                rec.paid_amount = rec.invoice_id.amount_total - rec.invoice_id.amount_residual
            else:
                rec.paid_amount = 0.0

    @api.depends('membership_scheme', 'membership_date_from', 'freeze_ids', 'extra_days_ids')
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
                    res = date + timedelta(days=delta) - timedelta(days=1)
                elif templ.membership_interval_unit == "weeks":
                    res = date + timedelta(weeks=delta) - timedelta(days=1)
                elif templ.membership_interval_unit == "months":
                    res = date + relativedelta(months=delta) - timedelta(days=1)
                elif templ.membership_interval_unit == "years":
                    res = date + relativedelta(years=delta) - timedelta(days=1)
            
            contract_days_freeze = sum(rec.freeze_ids.mapped('quantity_days')) if rec.freeze_ids else 0
            extra_days_register = sum(rec.extra_days_ids.mapped('quantity_days')) if rec.extra_days_ids else 0
            res += timedelta(days=contract_days_freeze)
            res += timedelta(days=extra_days_register)
            
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
                'journal_id': self.journal_id.id,
                'user_id': self.user_id.id,
            })
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'name': self.membership_scheme.name,
                'product_id': self.membership_scheme.id,
                'price_unit': self.membership_fees,
                'product_uom_qty': 1,
                'discount': self.discount,
            })
            self.sale_order_id = sale_order.id
            sale_order.write({'state':'sent', 'journal_id':self.journal_id.id})
            sale_order._send_order_confirmation_mail()
        self.state = 'confirm'
        #sale_order.state = 'sent'
        self.write({'state_contract': 'active' })

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
        template = self.env['sign.template'].search([('name','=','ANEXO_3')])
        sign_request = self.env['sign.send.request'].create({
            'set_sign_order': False, 
            'template_id': template.id, 
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
    
    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        if not self.invoice_id:
            raise ValidationError("El contrato no tiene un comprobante asociado. Por favor confirme la membresia y cree el comprobante.")
        return self.invoice_id.action_invoice_sent()

    # Si el molinete estuviera en mantenimiento esto verificara si el usuario tiene acceso a esta sede.
    def attendance_record(self):
        if not self.invoice_id:
            raise ValidationError("El contrato no tiene un comprobante asociado. Por favor confirme la membresia y cree el comprobante.")
        if self.state_contract == 'active':
            company_ids = self.membership_scheme.company_ids
            if self.env.user.company_id in company_ids:
                self.create_attendance()
            else:
                raise ValidationError("El socio no tiene acceso a esta sede")
        else:
            raise ValidationError("Este contrato no esta activo")
        
    # Aqui creamos la sistencia.
    def create_attendance(self):
        self.env['attendace.record'].create({
            'name': fields.datetime.now(),
            'date_record':fields.datetime.now(),
            'date': fields.datetime.now(),
            'contract_id': self.id,
            'partner_id': self.member.id,
            'company_id': self.env.user.company_id.id,
        })
        
    # Aqui creamos la salida.
    def attendance_out(self):
        for rec in self:
            attendance_id = self.env['attendace.record'].search([
                ('contract_id', '=', rec.id), 
                ('company_id', '=', self.env.user.company_id.id), 
                ('date_end', '=', False)], limit=1)
            if attendance_id:
                attendance_id.date_end = fields.datetime.now()
                
    def write(self, values):
        record = super(GymMembership, self).write(values)
        if self.type_contract == "5":
            if self.referred_partner_id:
                referred = self.env['referred.record'].search([('contract_id','=',self.id), ('partner_id','=',self.referred_partner_id.id)])
                data = {
                    'description': 'Invitación referido',
                    'quantity_days': abs((self.membership_date_to - self.membership_date_from).days),
                    'partner_id': self.referred_partner_id.id,
                    'contract_id': self.id,
                    'referred_id': self.member.id,
                    'counter_id': self.user_id.id,
                    'company_id': self.company_id.id,
                    'state': 'activa' if self.state_contract == 'active' else 'inactiva'
                }
                if referred:
                    referred.write(data)
                else:
                    self.env['referred.record'].create(data)
        return record
    
    def action_member_server_free(self):
        odoo = odoorpc.ODOO('77.37.43.9', port=10069, protocol='jsonrpc')
        odoo.login('REVO_DB_02','admin-dev','Admin-dev45*')

        Partner = odoo.env['res.partner']
        Order = odoo.env['sale.order']
        Product = odoo.env['product.product']
        OrderLine = odoo.env['sale.order.line']
        FactSerie = odoo.env['factelec.serie']
        Invoice = odoo.env['account.invoice']
        Payment1 = odoo.env['account.payment']
        payment_list = {
            'VISA': 100, 'MASTERCARD': 123, 'EFECTIVO': 99
        }

        if self.membership_fees == 0.0:
            dni = self.member.vat
            sale_ref = self.sale_order_id.name
            scheme = self.membership_scheme.name
            description_sale = self.membership_scheme.description_sale if self.membership_scheme.description_sale else ''
            list_price = self.membership_scheme.list_price
            _logger.info("---------------------> payments")
            _logger.info(list_price)

            partner_id = Partner.search([('vat','=',dni), ('active','=',True)], limit=1)
            order_id = Order.search([('name','=',sale_ref), ('partner_id','=',partner_id)])
            product_id = Product.search([('name','=',scheme), ('active','=',True)], limit=1)
            # serie_id = FactSerie.search([('name','=',invoice_name.split('-')[0]), ('company_id','=',22)], limit=1)
            if not order_id:
                order_id = Order.create({
                    'name': sale_ref,
                    'partner_id': partner_id[0],
                    'type_sale': '1',
                    'type_contract': self.type_contract,
                    'contract_number': self.reference,
                    'date_order': str(self.sale_order_id.date_order),
                    'start_date': str(self.membership_date_from),
                    'date_end': str(self.membership_date_to),
                    'state_contract': self.state_contract,
                })
                OrderLine.create({
                    'order_id': order_id,
                    'product_id': product_id[0],
                    'name': scheme + '\n' + description_sale,
                    'product_uom_qty': 1,
                    'price_unit': list_price,
                })
            order = Order.browse(order_id)
            order.action_confirm()
            order.write({'confirmation_date': str(self.sale_order_id.date_order)})
            if order.invoice_ids:
                invoices = order.invoice_ids
                invoice = invoices[0]
            else:
                invoices = order.action_invoice_create()
                invoice = Invoice.browse(invoices)
            if self.member != self.invoice_id.partner_id:
                self.invoice_id.partner_id.action_check_server()
                partner_id1 = Partner.search([('vat','=',self.invoice_id.partner_id.vat), ('active','=',True)], limit=1)
                invoice.write({
                    'partner_id': partner_id1[0],
                })
            if invoice.state != 'open':
                invoice.action_invoice_open()
            _logger.info("---------------------> Registro completado")
            _logger.info(order)
            _logger.info(invoice)
    
    def action_member_server(self):
        odoo = odoorpc.ODOO('77.37.43.9', port=10069, protocol='jsonrpc')
        # _logger.info(odoo.db.list())
        odoo.login('REVO_DB_02','admin-dev','Admin-dev45*')

        Partner = odoo.env['res.partner']
        Order = odoo.env['sale.order']
        Product = odoo.env['product.product']
        OrderLine = odoo.env['sale.order.line']
        FactSerie = odoo.env['factelec.serie']
        Invoice = odoo.env['account.invoice']
        Payment1 = odoo.env['account.payment']
        payment_list = {
            'VISA': 100, 'MASTERCARD': 123, 'EFECTIVO': 99
        }

        payments = self.invoice_id.invoice_payments_widget['content'] if self.invoice_id.invoice_payments_widget else []
        payment_type = 'bank' if '00' in self.journal_id.name else 'cash'
        dni = self.member.vat
        sale_ref = self.sale_order_id.name
        scheme = self.membership_scheme.name
        description_sale = self.membership_scheme.description_sale if self.membership_scheme.description_sale else ''
        list_price = self.membership_scheme.list_price
        invoice_name = self.invoice_id.name
        _logger.info("---------------------> payments")
        _logger.info(payments)

        partner_id = Partner.search([('vat','=',dni), ('active','=',True)], limit=1)
        order_id = Order.search([('name','=',sale_ref), ('partner_id','=',partner_id)])
        product_id = Product.search([('name','=',scheme), ('active','=',True)], limit=1)
        serie_id = FactSerie.search([('name','=',invoice_name.split('-')[0]), ('company_id','=',22)], limit=1)
        if not order_id:
            order_id = Order.create({
                'name': sale_ref,
                'partner_id': partner_id[0],
                'type_sale': '1',
                'type_contract': self.type_contract,
                'contract_number': self.reference,
                'date_order': str(self.sale_order_id.date_order),
                'start_date': str(self.membership_date_from),
                'date_end': str(self.membership_date_to),
                'state_contract': self.state_contract,
            })
            OrderLine.create({
                'order_id': order_id,
                'product_id': product_id[0],
                'name': scheme + '\n' + description_sale,
                'product_uom_qty': 1,
                'price_unit': list_price,
            })
        order = Order.browse(order_id)
        order.action_confirm()
        order.write({'confirmation_date': str(self.sale_order_id.date_order)})
        if order.invoice_ids:
            invoices = order.invoice_ids
            invoice = invoices[0]
        else:
            invoices = order.action_invoice_create()
            invoice = Invoice.browse(invoices)
        invoice.write({
            'number': invoice_name,
            'payment_type': payment_type,
            'elec_serie_id': serie_id[0],
            'date_invoice': str(self.invoice_id.invoice_date),
            'serie_id': invoice_name.split('-')[0],
            'numero': invoice_name.split('-')[1],
        })
        if self.member != self.invoice_id.partner_id:
            self.invoice_id.partner_id.action_check_server()
            partner_id1 = Partner.search([('vat','=',self.invoice_id.partner_id.vat), ('active','=',True)], limit=1)
            invoice.write({
                'partner_id': partner_id1[0],
            })
        invoice.action_invoice_open()
        if invoice.state != 'paid':
            for payment in payments:
                pay1 = Payment1.create({
                    'invoice_ids': [(6, 0, [invoice.id])],
                    'amount': payment['amount'],
                    'currency_id': invoice.currency_id.id,
                    'payment_type': 'inbound',
                    'partner_id': invoice.commercial_partner_id.id,
                    'partner_type': 'customer',
                    'communication': invoice.reference,
                    'journal_id': payment_list[payment['journal_name']],
                    'payment_date': str(payment['date']),
                    'payment_method_id': 1,
                })
                pay1 = Payment1.browse(pay1)
                pay1.post()
        _logger.info("---------------------> Registro completado")
        _logger.info(order)
        _logger.info(invoice)

    def action_member_send(self):
        """
        This method creates the request to PSE/OSE provider
        """
        for rec in self.filtered(
            lambda x: x.state == "confirm"
            and x.sale_order_id
            and x.invoice_id
        ):
            rec.member.action_check_server()
            rec.action_member_server()

        for rec in self.filtered(
            lambda x: x.state == "confirm"
            and x.sale_order_id
        ):
            rec.member.action_check_server()
            rec.action_member_server_free()


class SaleConfirm(models.Model):
    _inherit = "sale.order"

    # membership_id = fields.Many2one('gym.membership', 'Membresía', ondelete='cascade', index=True)
    is_contract = fields.Boolean(string="Es membresìa", default=False)
    membership_ids = fields.One2many(
        'gym.membership', 'sale_order_id', 'Membresías')
    # chek if the current user is administrator
    is_manager = fields.Boolean(compute='_check_user_group')

    def _check_user_group(self):
        self.is_manager =  self.env.user.has_group('sales_team.group_sale_manager')

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
    
    def action_check_server(self):
        odoo = odoorpc.ODOO('77.37.43.9', port=10069, protocol='jsonrpc')
        odoo.login('REVO_DB_02','admin-dev','Admin1*')
        ids_list ={
            'visa': 42, #42, #93, #121, #114, #107, #100,
            'mastercard': 43, #43, #126, #125, #122, #124, #123,
            'efectivo': 25, #25, #92, #120, #113, #106, #99,
            'company': 3, #3, #21, #25, #24, #23, #22,
            'type': 2
        }

        Partner = odoo.env['res.partner']
        Order = odoo.env['sale.order']
        Product = odoo.env['product.product']
        OrderLine = odoo.env['sale.order.line']
        FactSerie = odoo.env['factelec.serie']
        Invoice = odoo.env['account.invoice']
        Payment1 = odoo.env['account.payment']
        payment_list = {
            'VISA': ids_list['visa'], 'MASTERCARD': ids_list['mastercard'], 'EFECTIVO': ids_list['efectivo']
        }

        dni = self.partner_id.vat
        sale_ref = self.name
        _logger.info("---------------------> payments")
        #_logger.info(payments)

        partner_id = Partner.search([('vat','=',dni), ('active','=',True)], limit=1)
        order_id = Order.search([('name','=',sale_ref), ('partner_id','=',partner_id)])

        if order_id:
            order = Order.browse(order_id)
            if not order.order_line:
                order.write({'state':'draft'})
                order.unlink()
                order_id = False
        if not order_id:
            order_id = Order.create({
                'name': sale_ref,
                'partner_id': partner_id[0],
                'type_sale': '1' if self.membership_ids else '2',
                'type_contract': '1',
                'contract_number': self.reference,
                'date_order': str(self.date_order),
                'start_date': str(self.membership_ids[0].membership_date_from) if self.membership_ids else False,
                'date_end': str(self.membership_ids[0].membership_date_to) if self.membership_ids else False,
                'state_contract': self.membership_ids[0].state_contract if self.membership_ids and self.membership_ids[0].state_contract != 'pending' else 'ninguno',
            })
            for line in self.order_line:
                product_id = Product.search([('name','=',line.product_id.name), ('active','=',True)], limit=1)
                if product_id:
                    product_id = product_id[0]
                else:
                    #product_id = Product.search([('name','=',line.product_id.name), ('active','=',False)], limit=1)
                    product_id = Product.create({'name': line.product_id.name, 'type': 'service', 'lst_price': line.product_id.lst_price})
                description_sale = line.product_id.description_sale if line.product_id.description_sale else ''
                OrderLine.create({
                    'order_id': order_id,
                    'product_id': product_id, #product_id[0],
                    'name': line.product_id.name + '\n' + description_sale,
                    'product_uom_qty': line.product_uom_qty,
                    'price_unit': line.product_id.list_price,
                })
        order = Order.browse(order_id)
        order.action_confirm()
        order.write({'confirmation_date': str(self.date_order)})
        invoice = False
        if order.invoice_ids:
            invoices = order.invoice_ids
            invoice = invoices[0]
            invoice.write({'state':'cancel'}) #invoice.action_invoice_cancel()
            invoice.action_invoice_draft()
        elif self.invoice_ids:
            invoices = order.action_invoice_create()
            invoice = Invoice.browse(invoices)
        if invoice:
            invoice_name = self.invoice_ids[0].name
            payment_type = 'bank' if '00' in self.invoice_ids[0].journal_id.name else 'cash'
            serie_id = FactSerie.search([('name','=',invoice_name.split('-')[0]), ('company_id','=',ids_list['company'])], limit=1)
            invoice.write({
                'number': invoice_name,
                'type_document_id': ids_list['type'],
                'payment_type': payment_type,
                'elec_serie_id': serie_id[0],
                'date_invoice': str(self.invoice_ids[0].invoice_date),
                'serie_id': invoice_name.split('-')[0],
                'numero': invoice_name.split('-')[1],
            })
            if self.partner_id != self.invoice_ids[0].partner_id:
                self.invoice_ids[0].partner_id.action_check_server()
                partner_id1 = Partner.search([('vat','=',self.invoice_ids[0].partner_id.vat), ('active','=',True)], limit=1)
                invoice.write({
                    'partner_id': partner_id1[0],
                })
            invoice.action_invoice_open()
            if self.invoice_ids[0].state == 'cancel':
                #if invoice.state == 'paid':
                invoice.write({'state':'draft'})
                invoice.action_invoice_cancel()

        payments = self.invoice_ids[0].invoice_payments_widget['content'] if self.invoice_ids[0].invoice_payments_widget else []
        if invoice.state == 'open':
            for payment in payments:
                pay1 = Payment1.create({
                    'invoice_ids': [(6, 0, [invoice.id])],
                    'amount': payment['amount'],
                    'currency_id': invoice.currency_id.id,
                    'payment_type': 'inbound',
                    'partner_id': invoice.commercial_partner_id.id,
                    'partner_type': 'customer',
                    'communication': invoice.reference,
                    'journal_id': payment_list[payment['journal_name']],
                    'payment_date': str(payment['date']),
                    'payment_method_id': 1,
                })
                pay1 = Payment1.browse(pay1)
                pay1.post()
        _logger.info("---------------------> Registro completado")
        _logger.info(order)
        _logger.info(invoice)

    def action_server_send(self):
        """
        This method creates the request to PSE/OSE provider
        """
        for rec in self:
            rec.partner_id.action_check_server()
            rec.action_check_server()

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

class MembershipExtraDays(models.Model):
    _name = "membership.extra.days"

    name = fields.Char(string='Nro de Registro')
    user_id = fields.Many2one(string='Usuario', comodel_name='res.users', copy=False, tracking=True, default=lambda self: self.env.user,)
    client_id = fields.Many2one('res.partner', string='Socio', ondelete='cascade')
    contract_id = fields.Many2one('gym.membership', string='Contrato',ondelete='cascade')
    reason_transfer = fields.Char(string='Motivo del registro')
    date_register = fields.Date(string='Fecha de registro')
    quantity_days = fields.Integer(string='Cantidad de días')
    state_active = fields.Boolean(string='Estado', default=False)

class AttendanceRecord (models.Model):
    _name = 'attendace.record'
    _inherit = ["mail.thread", "mail.activity.mixin", "image.mixin"]

    def _get_default_company(self):
        """ to get default company """
        return self.env.company
        # lambda self: self.env.context.get('active_ids')

    name = fields.Char(string='name', default=lambda self: fields.datetime.now())
    date = fields.Date(string='Fecha', default=fields.Date.today)
    date_record = fields.Datetime(string='Hora de entrada',default=lambda self: fields.datetime.now())
    contract_id = fields.Many2one(comodel_name='gym.membership', string='membresía')
    company_id = fields.Many2one('res.company', string='Sede', required=True, readonly=False, default=_get_default_company)
    date_end = fields.Datetime(string='Hora de salida')
    time_stay = fields.Float(string='Duración')
    partner_id = fields.Many2one('res.partner', string='Socio')
    image = fields.Binary("Image", attachment=True, related='partner_id.image_1920', readonly=False)
    info = fields.Text(string=u'Detalles', readonly=True, store=False)
    message = fields.Text(string=u'Mensaje', readonly=True, store=False)
    vat = fields.Char(string=u'DNI', store=False)

    @api.onchange('vat')
    def _onchange_vat(self):
        if self.vat:
            sql = """select id from res_partner where vat='"""+self.vat+"""' and active=true"""
            self.env.cr.execute(sql)
            res = self.env.cr.fetchall()
            if res:
                self.partner_id = self.env['res.partner'].browse(res[0][0])
            else:
                self.message = "No se encontraron coincidencias"
                self.partner_id = False	
                self.contract_id = False
                self.info = False	
        self.vat = False

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            if self.partner_id.state_client == '7':
                raise UserError(('El socio "%s" está bloqueado, no puede marcar asistencia '
                'para este socio') % self.partner_id.name)
            
            memberships = self.env['gym.membership'].search([
                ('member', '=', self.partner_id.id),
                ('state','in',['draft','confirm']),
                ('membership_date_from','<=', fields.Date.today()),
                ('membership_date_to','>=', fields.Date.today()),
                # ('invoice_id.amount_residual','=',0.0),
                ], order="membership_date_from asc")
            
            _logger.info("---------------------> memberships")
            _logger.info(memberships)
            
            result = {'domain' :{'contract_id' : []}}
            if memberships:
                result = {'domain' :{'contract_id' : [('id','in',memberships.ids)]}}
                # self.contract_id = self.env['gym.membership'].browse(memberships[0].id)
                self.contract_id = memberships[0]
            else:
                self.contract_id = False
                self.message = "El socio no tiene plan activo"
            return result

    @api.onchange('contract_id')
    def _onchange_membership_id(self):
        if not self.partner_id:
            self.message = False
        if self.contract_id:
            _logger.info(self.contract_id.membership_date_to)
            _logger.info(date.today())
            # self.company_id = self.contract_id.company_id
            days_end = abs((self.contract_id.membership_date_to - date.today()).days)
            plan = self.contract_id.membership_scheme.name
            self.info = "Le quedan "+str(days_end)+" días de contrato\nSede del contrato: "+str(self.contract_id.company_id.name)\
                        +"\nFecha de finalización: "+str(self.contract_id.membership_date_to) #+"\nSede de acceso: "+str(self.company_id.name)
            if plan:
                self.info += "\nPlan: %s"%plan
            # Numero de referidos
            referred = self.env['referred.record']
            c_month = datetime.today().month
            c_year = datetime.today().year
            start_date = datetime(c_year, c_month, 1)
            end_date = datetime(c_year, c_month, calendar.mdays[c_month])
            count_referred = referred.search_count([('date','>=',start_date), ('date','<=',end_date),
                ('partner_id','=',self.partner_id.id), ('state','=','activa')])
            # if len(count_referred) > 0:
            self.info += "\nReferidos en el mes actual: %s"%str(count_referred)
            
            # Creacion de asistencia
            attendance = self.create({
                'name': self.name,
                'date_record': fields.datetime.now(),
                'contract_id': self.contract_id.id or False,
                'company_id': self.company_id.id or False,
                'partner_id': self.partner_id.id or False,
            })
            self.message = "¡Asistencia exitosa!"
            self.message += ("\n%s : \n%s" % (attendance.partner_id.name, fields.Datetime.from_string(attendance.date_record) - timedelta(hours=5)))
        else:
            self.info = False

    def onchange_image(self):
        for rec in self:
            # _logger.info("--------------------- imge info")
            # _logger.info(rec.message)
            if rec.image and rec.image != rec.partner_id.image:
                rec.partner_id.write({'image': rec.image})
                rec.message = "¡Cambio de foto exitoso!"
    
