from odoo import fields, models, api
import datetime
from dateutil.relativedelta import relativedelta
from ..reports.report_inv_bal import ReportInvBalTxt, ReportInvBalExcel
import base64
from odoo.tools.float_utils import float_round
from odoo.exceptions import ValidationError


class PleInvBalInitial07(models.Model):
    _inherit = 'ple.report.inv.bal.07'

    line_initial_ids = fields.One2many(
        comodel_name='ple.inv.bal.line.initial.balances.07',
        inverse_name='ple_report_inv_val_id',
        string='Líneas'
    )
    line_final_ids = fields.One2many(
        comodel_name='ple.inv.bal.line.final.balances.07',
        inverse_name='ple_report_inv_val_id',
        string='Líneas'
    )

    def action_generate_initial_whit_ending_balances_07(self):
        data = False
        documents = self.env['ple.report.inv.bal.07'].search([
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
                        (0, 0, {'product_id': obj_line.product_id,
                                'stock_catalog': obj_line.stock_catalog,
                                'stock_type': obj_line.stock_type,
                                'code_catalog_used': obj_line.code_catalog_used,
                                'unspsc_code_id': obj_line.unspsc_code_id,
                                'product_description': obj_line.product_description,
                                'quantity_product_hand': obj_line.quantity_product_hand,
                                'product_udm': obj_line.product_udm,
                                'property_cost_method': obj_line.property_cost_method,
                                'standard_price': obj_line.standard_price,
                                'total': obj_line.total,
                                'default_code': obj_line.default_code,
                                'ple_report_inv_val_id': self.id,
                                }),
                    ]
                })
        return data

    def action_generate_initial_balances_07(self):
        self.line_initial_ids.unlink()
        account_query = """
                        SELECT aa.id
                         -- QUERIES TO MATCH MULTI TABLES
                            FROM account_account as aa
                        --  TYPE JOIN   |  TABLE                        | MATCH
                            INNER JOIN     account_group as ag            ON aa.group_id = ag.id
                        -- FILTER QUERIES 
                            WHERE ag.code_prefix_start in ('20','21');                   
                """
        self.env.cr.execute(account_query)
        val_account = self.env.cr.dictfetchall()

        if not val_account:
            self.write({'error_dialog': 'No hay cuentas configuradas con Prefijo de código 20 y 21'})
            return True
        acc_q = []
        for i in val_account:
            acc_q.append(i['id'])

        query = """        
        SELECT
        pp.id as product_id,
        pp.default_code as default_code,
        pt.stock_catalog as stock_catalog,
        pt.stock_type as stock_type,
        pt.unspsc_code_id as unspsc_code_id,
        CASE WHEN pt.unspsc_code_id != NULL then '1' ELSE ''  END AS code_catalog_used,
        pt.name as product_description,
        uu.l10n_pe_edi_measure_unit_code as product_udm,
        {ple_report_inv_val_id} as ple_report_inv_val_id,
        svl.company_id as company_id,
        SUM(svl.quantity) as quantity_product_hand,
        SUM(svl.value) as total,
        MAX(svl.accounting_date) as last_date 
        
        FROM stock_valuation_layer svl
        
        LEFT JOIN product_product pp 	  ON svl.product_id=pp.id
        LEFT JOIN product_template pt 	  ON pp.product_tmpl_id= pt.id
        LEFT JOIN uom_uom uu 			  ON pt.uom_id= uu.id
        LEFT JOIN product_unspsc_code puc ON pt.unspsc_code_id=puc.id
        LEFT JOIN account_move   am	 	  ON svl.account_move_id=am.id
        LEFT JOIN account_account aa      ON am.pay_sell_force_account_id=aa.id
        LEFT JOIN account_group    ag     ON aa.group_id=ag.id
        
        WHERE svl.accounting_date<='{date_end}' AND svl.accounting_date>='{date_start}'
        AND svl.company_id = {company_id} 
        GROUP BY pp.id,pt.stock_catalog,pt.stock_type,pt.unspsc_code_id,pt.name,
        uu.l10n_pe_edi_measure_unit_code,svl.company_id
        ORDER BY pp.id DESC  
        """.format(
            company_id=self.company_id.id,
            date_start=self.date_start - relativedelta(years=1),
            date_end=self.date_end - relativedelta(years=1),
            date_self=self.date_end.strftime('%Y%m%d'),
            ple_report_inv_val_id=self.id,
            accounts=tuple(acc_q),
        )

        try:
            self.env.cr.execute(query)
            values = self.env.cr.dictfetchall()
            lines_data = {}

            for val in values:

                product = self.env['product.product'].search([('id', '=', val['product_id'])])
                if val['quantity_product_hand']>0:
                    val.setdefault('standard_price', val['total']/val['quantity_product_hand'])
                else:
                    val.setdefault('standard_price',0)

            lines_report = list(lines_data.values())

            self.env['ple.inv.bal.line.initial.balances.07'].create(lines_report)

        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

    def action_generate_initial_balances_307(self):
        data = self.action_generate_initial_whit_ending_balances_07()

        if data:
            pass
        else:
            self.action_generate_initial_balances_07()
        return

    def capture_initial_balances_id(self):
        lasx = []
        for i in self.line_initial_ids:
            values = {
                'product_id' : i.product_id,
                'period' : i.period,
                'stock_catalog': i.stock_catalog,
                'stock_type' : i.stock_type,
                'default_code' : i.default_code,
                'unspsc_code_id':i.unspsc_code_id,
                'code_catalog_used':i.code_catalog_used,
                'quantity_product_hand':i.quantity_product_hand,
                'standard_price': i.standard_price,
                'product_udm':i.product_udm,
                'property_cost_method': i.property_cost_method,
                'product_description': i.product_description,
                'last_date':i.last_date,
                'total':i.total
            }
            lasx.append(values)
        return list(lasx)


class PleInvBalLinesInitial07(models.Model):
    _name = 'ple.inv.bal.line.initial.balances.07'
    _description = 'Estado de Situación financiera de saldos iniciales - Líneas'

    ple_report_inv_val_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.07',
        string='Reporte de Estado de Situación financiera'
    )
    period=fields.Char(string="periodo")
    stock_catalog = fields.Char(string='Código de catálogo')
    stock_type = fields.Char(string='Tipo de Existencia')
    default_code = fields.Char(string="Código propio de la existencia")
    code_catalog_used = fields.Char(string="codigo catalogo utilizado")
    unspsc_code_id = fields.Integer(string="UNSPSC Codigo")
    product_id = fields.Char(string='Product_id')
    product_description = fields.Char(string='Producto')
    product_udm = fields.Char(string='UDM')
    quantity_product_hand = fields.Float(string='Cantidad a mano')
    standard_price = fields.Float(string='Costo Unitario')
    property_cost_method=fields.Char(string="Property cost method")
    aml_id = fields.Integer(string='aml valuation')
    total = fields.Float(string="Total")
    company_id = fields.Integer(string='Company id')
    last_date = fields.Date(string="Dia del ultimo registro ")


class PleInvBalLinesFinal07(models.Model):
    _name = 'ple.inv.bal.line.final.balances.07'
    _description = 'Estado de Situación financiera de saldos iniciales - Líneas'

    ple_report_inv_val_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.07',
        string='Reporte de Estado de Situación financiera'
    )
    period = fields.Char(string="periodo")
    stock_catalog = fields.Char(string='Código de catálogo')
    stock_type = fields.Char(string='Tipo de Existencia')
    default_code = fields.Char(string="Código propio de la existencia")
    code_catalog_used = fields.Char(string="codigo catalogo utilizado")
    unspsc_code_id = fields.Integer(string="UNSPSC Codigo")
    product_id = fields.Char(string='Product_id')
    product_description = fields.Char(string='Producto')
    product_udm = fields.Char(string='UDM')
    quantity_product_hand = fields.Float(string='Cantidad a mano')
    standard_price = fields.Float(string='Costo Unitario')
    property_cost_method = fields.Char(string="Property cost method")
    aml_id = fields.Integer(string='aml valuation')
    total = fields.Float(string="Total")
    company_id = fields.Integer(string='Company id')
    last_date = fields.Date(string="Dia del ultimo registro ")

    ple_report_inv_val_07_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.07',
        string='Reporte de Estado de Situación financiera'
    )