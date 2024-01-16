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

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class GymMembership(models.Model):
    _name = "gym.membership"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Gym Membership"
    _rec_name = "reference"

    reference = fields.Char(string='Referencia', required=True,
                            readonly=True, default=lambda self: _('New'))
    member = fields.Many2one('res.partner', string='Socio', required=True,
                             tracking=True,
                             domain="[('gym_member', '!=',False)]")
    membership_scheme = fields.Many2one('product.product',
                                        string='Esquema de membresía',
                                        required=True, tracking=True)
    paid_amount = fields.Integer(string="Monto pagado", tracking=True)
    membership_fees = fields.Float(string="Cuotas de membresía", tracking=True,
                                   related="membership_scheme.list_price")
    sale_order_id = fields.Many2one('sale.order', string='Orden de venta',
                                    ondelete='cascade', copy=False,
                                    readonly=False)
    invoice_id = fields.Many2one('account.move', string='Factura',
                                    ondelete='cascade', copy=False,
                                    readonly=False)
    membership_date_from = fields.Date(string='Fecha de inicio de la membresía',
                                       default=datetime.today(),
                                       help='Date from which membership becomes active.')
    membership_date_to = fields.Date(string='Fecha de vencimiento de la membresía',
                                     compute="_compute_membership_date_to",
                                     help='Date until which membership remains active.')

    _sql_constraints = [
        ('membership_date_greater',
         'check(membership_date_to >= membership_date_from)',
         'Error ! Ending Date cannot be set before Beginning Date.')
    ]
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancelled', 'Cancelled')
    ], default='draft', string='Status')

    @api.depends('membership_scheme', 'membership_date_from')
    def _compute_membership_date_to(self):
        """ to get membership_date_to """
        res = self.membership_date_from
        templ = self.membership_scheme.product_tmpl_id
        if templ.membership_type == "variable":
            delta = templ.membership_interval_qty
            date = fields.Date.from_string(self.membership_date_from)
            if templ.membership_interval_unit == "days":
                res = date + timedelta(days=delta)
            elif templ.membership_interval_unit == "weeks":
                res = date + timedelta(weeks=delta)
            elif templ.membership_interval_unit == "months":
                res = date + relativedelta(months=delta)
            elif templ.membership_interval_unit == "years":
                res = date + relativedelta(years=delta)
            
        # date_to = self.membership_scheme._get_next_date(self.membership_date_from, qty=1)
        self.membership_date_to = res

    @api.model
    def create(self, vals):
        """ sequence number for membership """
        if vals.get('reference', ('New')) == ('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'gym.membership') or ('New')
        res = super(GymMembership, self).create(vals)
        return res
    
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


class SaleConfirm(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """ membership  created directly from sale order confirmed """
        product = self.env['product.product'].search([
            ('membership_date_from', '!=', False),
            ('id', '=', self.order_line.product_id.id)])
        for record in product:
            self.env['gym.membership'].create([
                {'member': self.partner_id.id,
                 'membership_date_from': record.membership_date_from,
                 'membership_scheme': self.order_line.product_id.id,
                 'sale_order_id': self.id,
                 }])

        res = super(SaleConfirm, self).action_confirm()
        return res
