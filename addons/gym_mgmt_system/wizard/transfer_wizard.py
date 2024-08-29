# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo.tools.translate import _
from odoo.tools import email_split
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models
from datetime import datetime, date, timedelta

import logging
_logger = logging.getLogger(__name__)


class TransferWizard(models.TransientModel):
    """
        A wizard to manage the creation/removal of transfer membership.
    """
    _name = 'transfer.wizard'
    _description = 'Grant Transfer Membership'

    def _default_membership(self):
        return self.env['gym.membership'].browse(self._context.get('active_id'))

    contract_id = fields.Many2one(comodel_name='gym.membership', string='Membresía', default=_default_membership, readonly=True)
    number_transfer = fields.Char(string='Nro de Solicitud', required=True)
    client_id = fields.Many2one(comodel_name='res.partner', string='Socio a transferir',required=True)
    reason_transfer = fields.Char(string='Motivo de la transferencia')
    date_transfer = fields.Date(string='Fecha de la transferencia', default=datetime.today())
    days_transferred = fields.Integer(string='Días disponibles', compute="_get_days_avilable")
    discount = fields.Float(string="Descuento (%)", digits='Discount')
    authorize_user = fields.Many2one(comodel_name='res.users', string="Autoriza")

    @api.depends('contract_id')
    def _get_days_avilable(self):
        ope_1 = self.contract_id.membership_date_to - datetime.today().date()
        # ope_1 = (datetime.strptime(self.contract_id.membership_date_to, "%Y-%m-%d") - datetime.today())
        self.days_transferred =  (ope_1 + timedelta(days=1)).days

    #Esta función crea la transferencia vendida.
    def create_transfer(self):
        self.ensure_one()
        days_limit = self.days_transferred
        #Buscamos un contrato activo y que pertenezca al cliente seleccionado
        contract_client = self.env['gym.membership'].search(
            [('member', '=', self.client_id.id),('state_contract','=','active'),('membership_date_to','>',datetime.today())], limit=1)

        #Si la busqueda "contract_client" encuentra un contrato esto significa que el contrato creado estara habil despues de que el cliente termine su contrato actual
        if contract_client:
            start = contract_client.membership_date_to + timedelta(days=1)
            end = start + timedelta(days=days_limit)
        #Caso contrario el nuevo contrato comenzara desde el día siguiente.
        else:
            start = datetime.today() + timedelta(days=1)
            end = start + timedelta(days=days_limit)

        #Procedemos a crear la nueva membresia jalando datos del contrato seleccionado y de los datos que designamos con anterioridad.
        membership2 = self.env['gym.membership'].create({
            'reference': _('New'),
            'member': self.client_id.id,
            'type_contract': "3",
            'membership_date_from': start,
            'days_transferred':days_limit,
            'membership_date_to': end,
            'state_contract': "inactive",
            'membership_scheme': self.contract_id.membership_scheme.id,
            'journal_id': self.contract_id.journal_id.id,
            'authorize_user': self.authorize_user.id,
            'discount': self.discount,
            'membership_fees': 80,
        })
        #Realizamos la creación de la transferencia
        self.env['membership.transfer'].create({
            'number_transfer': self.number_transfer,
            'contract_id': self.contract_id.id,
            'client_id': self.client_id.id,
            'contract2_id': membership2.id,
            'client2_id': self.contract_id.member.id,
            'reason_transfer': self.reason_transfer,
            'date_transfer': self.date_transfer,
            'days_transferred': days_limit,
            'currente_transfer': start,
        })

        #Realizamos la creación de las ordenes de linea. Recorremos la anterior venta y adjuntamos la membresia del contrato a transferir con la diferencia que este cuesta 80 nuevos soles
        # membership2.create_membership_sale()
        sale_order = self.env['sale.order'].create({
            'partner_id': self.client_id.id,
            'is_contract': True,
            'journal_id': self.contract_id.journal_id.id,
        })
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'name': 'TRASPASO',
            'product_id': self.contract_id.membership_scheme.id,
            'price_unit': 80,
            'product_uom_qty': 1,
            'discount': self.discount,
        })
        membership2.sale_order_id = sale_order.id
        # membership2.state = 'confirm'

        #Ahora solo queda dar debaja este contrato.
        self.contract_id.membership_date_to = datetime.today()
        self.contract_id.state_contract = 'inactive'

        #Si todo el proceso esta ok retornamos true
        action = self.env.ref('gym_mgmt_system.action_gym_membership').read()[0]
        form_view = [(self.env.ref('gym_mgmt_system.view_membership_form').id, 'form')]
        action['views'] = form_view
        action['res_id'] = membership2.id
        return action
        # return True
