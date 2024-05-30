from odoo import fields, models, api
import datetime
from dateutil.relativedelta import relativedelta
import base64
from odoo.exceptions import ValidationError


class PleInvBalInitial(models.Model):
    _inherit = 'ple.report.inv.bal.08'

    line_initial_ids = fields.One2many(
        comodel_name='ple.inv.bal.line.initial.balances.08',
        inverse_name='ple_report_inv_val_id',
        string='Líneas'
    )
    line_final_ids = fields.One2many(
        comodel_name='ple.inv.bal.line.final.balances.08',
        inverse_name='ple_report_inv_val_id',
        string='Líneas'
    )

    def action_generate_initial_whit_ending_balances(self):
        data = False
        documents = self.env['ple.report.inv.bal.08'].search([
            ('date_start', '>=', self.date_start - relativedelta(years=1)),
            ('date_end', '<=', self.date_start),
            ('company_id', '=', self.company_id.id),
            ('state', 'in', ('load', 'closed')),
        ], limit=1)
        if documents:
            data = True
            self.write({
                'line_initial_ids': [(5, 0, 0)],
            })
            for obj_line in documents.line_final_ids:
                self.write({
                    'line_initial_ids': [
                        (0, 0, {'camp_id': obj_line.camp_id,
                                'state': obj_line.state,
                                'name': obj_line.name,
                                'catalog_code': obj_line.catalog_code,
                                'document_name': obj_line.document_name,
                                'correlative': obj_line.correlative,
                                'type_document_transmitter': obj_line.type_document_transmitter,
                                'number_document_transmitter': obj_line.number_document_transmitter,
                                'transmitter_name': obj_line.transmitter_name,
                                'title_code': obj_line.title_code,
                                'title_unit_value': obj_line.title_unit_value,
                                'total_amount_value': obj_line.total_amount_value,
                                'total_title_costs': obj_line.total_title_costs,
                                'total_title_provision': obj_line.total_title_provision,
                                'free_camp': obj_line.free_camp,
                                'ple_report_inv_val_id': self.id,
                                }),
                    ]
                })
        return data

    def action_generate_initial_balances(self):
        self.line_initial_ids.unlink()
        account_query = """
                SELECT aa.id
                 -- QUERIES TO MATCH MULTI TABLES
                    FROM account_account as aa
                -- FILTER QUERIES 
                    WHERE 
                    aa.ple_selection = 'investment_property_cost_3_8' OR 
                    aa.ple_selection = 'investment_property_provision_3_8';                     
        """
        self.env.cr.execute(account_query)
        val_account = self.env.cr.dictfetchall()

        if not val_account:
            self.write(
                {'error_dialog': 'No hay cuentas configuradas con Prefijo de código 11'})
            return True

        acc_q = []
        for i in val_account:
            acc_q.append(i['id'])

        query = """
        SELECT
                '{date_self}' AS name,
                '{financial_statements_catalog}' as catalog_code,
                aml.id as camp_id,
                am.name as document_name,
                aml.ple_correlative as correlative,
                llit.l10n_pe_vat_code as type_document_transmitter,
                rp.vat as number_document_transmitter,
                rp.name as transmitter_name,
                CASE WHEN aa.ple_selection='investment_property_provision_3_8' then 0  
                ELSE ai.title_unit_value   END as title_unit_value,
                ai.title_code as title_code,
                CASE WHEN aa.ple_selection='investment_property_provision_3_8' then '0.00'  
                ELSE ai.total_amount_value END as total_amount_value,
                aml.partner_id as partner_id,
                UDF_numeric_char(sum(aml.balance)) as total_title_costs,
                {ple_report_inv_val_id} as ple_report_inv_val_id
                
            -- QUERIES TO MATCH MULTI TABLES
                FROM account_move_line as aml
            --  TYPE JOIN   |  TABLE                        | MATCH
                LEFT JOIN    account_account as aa                  ON aml.account_id = aa.id           
                LEFT JOIN    account_group as ag                    ON aa.group_id = ag.id
                LEFT JOIN    res_partner as rp                      ON aml.partner_id = rp.id
                LEFT JOIN    account_move as am                     ON aml.move_id = am.id
                LEFT JOIN    asset_intangible ai                    ON aml.asset_intangible_id = ai.id
                LEFT JOIN    l10n_latam_identification_type as llit ON llit.id = rp.l10n_latam_identification_type_id
            -- FILTER QUERIES 
                WHERE aa.ple_selection LIKE 'investment_property_cost_3_8'  and
                aml.date >= '{date_start}' AND 
                aml.date <= '{date_end}' AND
                aml.company_id = {company_id} AND
                ("aml"."account_id" in                 
                (SELECT aa.id
                 -- QUERIES TO MATCH MULTI TABLES
                    FROM account_account as aa
                -- FILTER QUERIES 
                    WHERE 
                    aa.ple_selection = 'investment_property_cost_3_8' OR 
                    aa.ple_selection = 'investment_property_provision_3_8')           
                    )
                GROUP BY
                    number_document_transmitter, transmitter_name, correlative,
                    type_document_transmitter, document_name, title_code, 
                    title_unit_value, total_amount_value, ple_selection,
                    camp_id, aml.partner_id;
        """.format(
            company_id=self.company_id.id,
            date_start=self.date_start - relativedelta(years=1),
            date_end=self.date_end - relativedelta(years=1),
            state='posted',
            financial_statements_catalog=self.financial_statements_catalog,
            date_self=self.date_end.strftime('%Y%m%d'),
            accounts=tuple(acc_q),
            ple_report_inv_val_id=self.id
        )

        try:
            self.env.cr.execute(query)
            values = self.env.cr.dictfetchall()
            for dict in values:
                if dict['partner_id']:
                    dict.setdefault('total_title_provision',
                                    self.set_sum_total_title_provision_initial_balance(dict['partner_id']))
                    dict.setdefault('state', '1')

            lines_report = list(values)
            self.env['ple.inv.bal.line.initial.balances.08'].create(
                lines_report)

        except Exception as error:
            raise ValidationError(
                f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

    def set_sum_total_title_provision_initial_balance(self, partner_id):
        mount = False
        if partner_id:
            assets_query = f"""
                SELECT  sum(aml.balance) as title_provision
                -- QUERIES TO MATCH MULTI TABLES
                    FROM account_move_line as aml
                    LEFT JOIN    account_account as aa  ON aml.account_id = aa.id
                -- FILTER QUERIES 
                    WHERE aa.ple_selection = 'investment_property_cost_3_8' OR aa.ple_selection = 'investment_property_provision_3_8' AND
                    aml.date < '{self.date_start}' AND
                    aml.partner_id = {partner_id} AND
                    aml.balance < 0;                   
                """

            self.env.cr.execute(assets_query)
            mount = self.env.cr.dictfetchall()
        if mount:
            return mount[0]['title_provision'] if mount[0]['title_provision'] is not None else '0.00'
        else:
            return '0.00'

    def action_generate_initial_balances_308(self):
        data = self.action_generate_initial_whit_ending_balances()
        if data:
            pass
        else:
            self.action_generate_initial_balances()
        return

    def capture_initial_balances_id(self):
        quantity_hand = dict()
        for obj in self.line_initial_ids:
            quantity_hand[obj.camp_id] = {}
            quantity_hand[obj.camp_id]['camp_id'] = obj.camp_id
            quantity_hand[obj.camp_id]['state'] = obj.state
            quantity_hand[obj.camp_id]['name'] = obj.name
            quantity_hand[obj.camp_id]['catalog_code'] = obj.catalog_code
            quantity_hand[obj.camp_id]['document_name'] = obj.document_name
            quantity_hand[obj.camp_id]['correlative'] = obj.correlative
            quantity_hand[obj.camp_id]['type_document_transmitter'] = obj.type_document_transmitter
            quantity_hand[obj.camp_id]['number_document_transmitter'] = obj.number_document_transmitter
            quantity_hand[obj.camp_id]['transmitter_name'] = obj.transmitter_name
            quantity_hand[obj.camp_id]['title_code'] = obj.title_code
            quantity_hand[obj.camp_id]['title_unit_value'] = obj.title_unit_value
            quantity_hand[obj.camp_id]['total_amount_value'] = obj.total_amount_value
            quantity_hand[obj.camp_id]['total_title_costs'] = obj.total_title_costs
            quantity_hand[obj.camp_id]['total_title_provision'] = obj.total_title_provision
            quantity_hand[obj.camp_id]['ple_report_inv_val_id'] = obj.ple_report_inv_val_id
            quantity_hand[obj.camp_id]['partner_id'] = obj.partner_id

        return quantity_hand


class PleInvBalLinesInitial08(models.Model):
    _name = 'ple.inv.bal.line.initial.balances.08'
    _description = 'Estimación de cuentas de cobranza dudosa de saldos iniciales - Líneas'
    _order = 'name desc'

    partner_id = fields.Integer(string="Id del partner_id")
    camp_id = fields.Char(string="Campo id del account move line")

    state = fields.Char(string='Indica el estado de la operación')
    name = fields.Char(string='Periodo')
    catalog_code = fields.Char(string='Código de catálogo')
    document_name = fields.Char(string='Nombre')
    correlative = fields.Char(string='Correlative')
    type_document_transmitter = fields.Integer(
        string="Tipo de documento del deudor"
    )
    number_document_transmitter = fields.Char(
        string="Numero de documento del transmisor"
    )
    transmitter_name = fields.Char(
        string="Razón social"
    )
    title_code = fields.Char(
        string="Código de titulo"
    )
    title_unit_value = fields.Integer(
        string="Valor unitario del titulo"
    )
    total_amount_value = fields.Char(
        string="Valor del monto total",
    )
    total_title_costs = fields.Float(
        string="Costo del monto total",
        digits=(16, 2)
    )
    total_title_provision = fields.Float(
        string="Provision total del titulo",
        digits=(16, 2)
    )
    free_camp = fields.Char(
        string="Campo libre"
    )
    ple_report_inv_val_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.08',
        string='Reporte de Estado de Situación financiera'
    )


class PleInvBalLinesFinal08(models.Model):
    _name = 'ple.inv.bal.line.final.balances.08'
    _description = 'Estimación de cuentas de cobranza dudosa de saldos finales - Líneas'
    _order = 'name desc'

    camp_id = fields.Char(string="Campo id del account move line")
    state = fields.Char(string='Indica el estado de la operación')
    name = fields.Char(string='Periodo')
    catalog_code = fields.Char(string='Código de catálogo')
    document_name = fields.Char(string='Nombre')
    correlative = fields.Char(string='Correlative')
    type_document_transmitter = fields.Integer(
        string="Tipo de documento del deudor"
    )
    number_document_transmitter = fields.Char(
        string="Numero de documento del transmisor"
    )
    transmitter_name = fields.Char(
        string="Razon social"
    )
    title_code = fields.Char(
        string="Código de titulo"
    )
    title_unit_value = fields.Integer(
        string="Valor unitario del titulo"
    )
    total_amount_value = fields.Char(
        string="Valor del monto total",
    )
    total_title_costs = fields.Float(
        string="Costo del monto total",
        digits=(16, 2)
    )
    total_title_provision = fields.Float(
        string="Provision total del titulo",
        digits=(16, 2)
    )
    transmitter_name = fields.Char(
        string="Razón social"
    )
    free_camp = fields.Char(
        string="Campo libre"
    )
    ple_report_inv_val_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.08',
        string='Reporte de Estado de Situación financiera'
    )
    ple_report_inv_val_08_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.08',
        string='Reporte de Estado de Situación financiera'
    )
