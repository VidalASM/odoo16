# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
import random
from datetime import datetime, date, timedelta

class CrmDraw(models.Model):
    _name = 'crm.draw'

    name = fields.Char(string=u'Título del sorteo')
    name_draw = fields.Char(string='Nombre de las oportunidades',required=True)
    date_draw = fields.Date(string='Fecha del sorteo', default=fields.Date.today)
    priority_opportunity = fields.Selection(string='Prioridad', selection=[('0', 'Normal'),('1', 'Baja'),('2', 'Alta'),('3', 'Muy alta'),], default='0')
    follow_up_days = fields.Integer(string='Días para el cierre', default=10, required=True)
    filter_draw = fields.Selection(string='Filtrar por',
        selection=[ ('1', 'Alianzado'), ('2', 'Espontáneo'), ('3', 'Invitado Espontáneo'),
                    ('4', 'Reinscripción'), ('5', 'Renovación'),('8', 'Invitado Referido'),('9', 'No atendido'),
                    ('happybirthday',u'Cumpleañeros de este mes'),('all', 'Todos') ], default='all', required=True)
    state = fields.Selection(string='Estado', selection=[('borrador', 'Borrador'), ('filtrado', 'Filtrado'),('sorteado','Sorteado')], default='borrador')
    company_id = fields.Many2one(comodel_name='res.company', string=u'Compañia',required=True)
    responsible_id = fields.Many2one(comodel_name='res.users', string='Responsable',default= lambda self: self.env.user, required=True, readonly=True)
    sales_ids = fields.Many2many(comodel_name='res.users', string='Vendedores',required=True)
    partner_ids = fields.Many2many(comodel_name='res.partner', string='Socios vinculados')
    date_end = fields.Date(string='Fecha del término (>=)')
    date_end_2 = fields.Date(string='Fecha del término (<=)')

    #Editamos el dominio de sales_ids y tambien le asignamos todos los vendodores de esa área
    @api.onchange('responsible_id')
    def _onchange_responsible_id(self):
        self.name = 'Sorteo de oportunidades %s'%(self.date_draw)
        self.company_id = self.responsible_id.company_id
        employees = self.env['hr.employee'].search(
                    [['company_id', '=', self.company_id.id],
                    ['department_id.name', '=', 'Ventas']])
        users = self.env['res.users'].search(
                    [['employee_ids', 'in', [employee.id for employee in employees]]])
        # result ={'domain': {'sales_ids': [('id', 'in', [user.id for user in users])]}}
        # self.sales_ids = users
        # return result

    #Filtramos para mostrar todos los socios que entraran el sorteo.
    def filters_draw(self):
        companies_child = self.env['res.company'].search([('id','child_of',[self.company_id.id])])
        companies_ids = [self.company_id.id]
        for comp_id in companies_child:
            companies_ids.append(comp_id.id)
        comp_str = ','.join([str(item) for item in companies_ids])
        if self.date_end and self.date_end_2:
            sql1 = """SELECT a.id
                    FROM res_partner a
                    LEFT JOIN gym_membership b on b.member = a.id
                    LEFT JOIN product_product p on b.membership_scheme = p.id
                    LEFT JOIN product_template t on t.id = p.product_tmpl_id
                    WHERE b.membership_date_to between '"""+str(self.date_end)+"""' and '"""+str(self.date_end_2)+"""'
                    AND b.company_id in ("""+comp_str+""")"""
            if self.filter_draw == 'happybirthday':
                sql1 += """ AND EXTRACT(MONTH FROM a.birthdate_date) = date_part('month', now()) 
                        AND a.state_client in ('1','2','3','4','5','8','9')"""
            elif self.filter_draw != 'all':
                sql1 += """ AND a.state_client = '"""+str(self.filter_draw)+"""'"""
        else:
            sql1 = """SELECT a.id
                    FROM res_partner a
                    LEFT JOIN gym_membership b on b.member = a.id
                    LEFT JOIN product_product p on c.membership_scheme = p.id
                    LEFT JOIN product_template t on t.id = p.product_tmpl_id
                    WHERE company_id in ("""+comp_str+""")"""
            if self.filter_draw == 'happybirthday':
                sql1 += """ AND EXTRACT(MONTH FROM a.birthdate_date) = date_part('month', now()) 
                        AND a.state_client in ('1','2','3','4','5','8','9')"""
            elif self.filter_draw != 'all':
                sql1 += """ AND a.state_client = '"""+str(self.filter_draw)+"""'"""
        # sql1 += """ ORDER BY t.val_days_temp desc """
        self.env.cr.execute(sql1)
        clients = self.env['res.partner'].search([['id', 'in', self._cr.fetchall()]])
        partners = []
        c_date = datetime.today().replace(day=1, hour=0, minute=0, second=0) + timedelta(hours=5)
        for client in clients: 
            # if client.opportunity_count == 0:
            if not client.opportunity_ids.filtered(lambda r:r.create_date > str(c_date)):
                partners.append(client.id)

        self.partner_ids = self.env['res.partner'].search([['id', 'in', partners]])
        self.state = 'filtrado'
        return True

    #Al confirmar el sorteo este creara las oportunidades y las sorteara entre los vendedores
    def confirm_draw(self):
        clients = [client for client in self.partner_ids]
        waste = []
        if len(clients)>=len(self.sales_ids):
            waste = waste + self.CreateOpportunity(clients,self.sales_ids)
        else:
            waste = waste + clients

        #Este while sirve para que no quede ningun cliente sin ser asignado a un vendedor.
        while len(waste) > 0:
            waste = self.CreateOpportunity(waste,self.sales_ids)

        self.state = 'sorteado'
        return True

    #Funcion para la creacion de una oportunidad y sortesos de esta.
    def CreateOpportunity(self,partners,users):
        waste = []
        #Asignamos los usuarios recibido a una array de sellers para no tener problemas con la lista "users"
        sellers = [user for user in users]
        try:
            promedio = int(len(partners)/len(sellers))
        except:
            raise exceptions.ValidationError(
                    u"No existen empleados en el departamento de Ventas")
        #Si el promedio es mayor a 0 eso indica que a cada vendedor se le asignara la misma cantidad de partner que los demas.
        if promedio > 0:
            for seller in sellers:
                for a in range(promedio):
                    partner = random.choice(partners)
                    self.CreateOpportunityEnv(partner,seller)
                    partners.remove(partner)
        #Si llegase a sobrar  partners este será asignado a una lista que sera sorteada al final
            if len(partners) > 0:
                for partner in partners:
                    waste.append(partner)
            return waste
        #Si el promedio es menor a 0 esto nos indica que por lo menos se asignara un cliente a cada usuario, los usuarios que se seleccionen sera de manera random.
        else:
            for partner in partners:
                seller = random.choice(sellers)
                self.CreateOpportunityEnv(partner,seller)
                sellers.remove(seller)
            return waste

    #Funcion para la creacion de oportunidades
    def CreateOpportunityEnv(self,client,user):
        self.env['crm.lead'].create({
        'name': "%s: %s"%(client.vat, self.name_draw),
        'partner_id': client.id,
        'type': 'opportunity',
        'priority': self.priority_opportunity,
        'date_deadline':datetime.today() + timedelta(days=self.follow_up_days),
        'company_id': self.company_id.id,
        'type_opportunity':self.filter_draw,
        'user_id': user.id,
        })

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    type_opportunity = fields.Selection(string='Tipo de oportunidad',
        selection=[ ('1', 'Alianzado'), ('2', 'Espontáneo'), ('3', 'Invitado Espontáneo'),
                    ('4', 'Reinscripción'), ('5', 'Renovación'),('8', 'Invitado Referido'),('9', 'No atendido'),
                    ('happybirthday',u'Cumpleañeros de este mes'),('all', 'Todos') ])
    membership_ids = fields.One2many('gym.membership', 'opportunity_id', 'Membresías')
    membership_count = fields.Integer(compute='_compute_membership_data', string="Número de Membresías")

    @api.depends('membership_ids')
    def _compute_membership_data(self):
        for lead in self:
            membership_cnt = 0
            # company_currency = lead.company_currency or self.env.company.currency_id
            for order in lead.membership_ids:
                if order.state_contract in ('pending', 'active'):
                    membership_cnt += 1
            lead.membership_count = membership_cnt

    def action_view_membership_quotation(self):
        action = self.env.ref('gym_mgmt_system.action_gym_membership').read()[0]
        action['context'] = {
            'search_default_draft': 1,
            'search_default_member': self.partner_id.id,
            'default_member': self.partner_id.id,
            'default_opportunity_id': self.id
        }
        action['domain'] = [('opportunity_id', '=', self.id), ('state_contract', 'in', ['pending', 'active'])]
        memberships = self.mapped('membership_ids').filtered(lambda l: l.state_contract in ('pending', 'active'))
        if len(memberships) == 1:
            action['views'] = [(self.env.ref('gym_mgmt_system.view_membership_form').id, 'form')]
            action['res_id'] = memberships.id
        return action


    # Esta funcion elimina las oportunidades que hayan superado el cierre previsto, ademas actualiza el estado del cliente si este no tiene otras oportunidades pendientes.
    @api.model
    def _delete_opportunity(self):
        opportunitys = self.search([
            ('date_deadline', '<', fields.Date.today()),
            ('stage_id.is_won','=',False),
            ('active','=',True)
        ])
        for opportunity in opportunitys:
            opportunity.write({
                'active': False
            })
            # if opportunity.partner_id.state_client not in ['6','3','8']:
            if opportunity.partner_id.state_client != "9":
                if opportunity.partner_id.opportunity_count == 0:
                    opportunity.partner_id.write({
                        'state_client': '9'
                    })

            # employees = self.env['hr.employee'].search([['company_id', '=', opportunity.company_id.id], ['department_id.name', '=', 'Ventas']])
            # users = self.env['res.users'].search([['employee_ids', 'in', [employee.id for employee in employees]], ['id','!=',opportunity.user_id.id]])
            users = self.env['res.users'].search([('company_id','=',opportunity.company_id.id), ('id','!=',opportunity.user_id.id)])
            list_users = [user for user in users]
            user = random.choice(list_users)
            self.env['crm.lead'].create({
                'name': "%s: Reasignado"%(opportunity.partner_id.vat),
                'partner_id': opportunity.partner_id.id,
                'type': 'opportunity',
                'priority': '0',
                'date_deadline':datetime.today() + timedelta(days=10),
                'company_id': opportunity.company_id.id,
                'type_opportunity':'9',
                'user_id': user.id,
            })
            #self.create_logstates(opportunity.partner_id.id,'9','No atendido')
