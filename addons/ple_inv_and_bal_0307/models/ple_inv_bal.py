from odoo import fields, models, api
from ..reports.report_inv_bal import ReportInvBalTxt, ReportInvBalExcel
import base64
import collections
from collections import defaultdict
from odoo.tools.float_utils import float_round
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class PleInvBal(models.Model):
    _name = 'ple.report.inv.bal.07'
    _description = 'Estado de Situación financiera'
    _inherit = 'ple.report.base'

    line_ids = fields.One2many(
        comodel_name='ple.report.inv.bal.line.07',
        inverse_name='ple_report_inv_val_07_id',
        string='Líneas'
    )
    financial_statements_catalog = fields.Selection(
        selection=[
            ('01', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR DIVERSAS - INDIVIDUAL'),
            ('02', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR SEGUROS - INDIVIDUAL'),
            ('03', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR BANCOS Y FINANCIERAS - INDIVIDUAL'),
            ('04', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - ADMINISTRADORAS DE FONDOS DE PENSIONES (AFP)'),
            ('05', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - AGENTES DE INTERMEDIACIÓN'),
            ('06', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - FONDOS DE INVERSIÓN'),
            ('07', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - PATRIMONIO EN FIDEICOMISOS'),
            ('08', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - ICLV'),
            ('09', 'OTROS NO CONSIDERADOS EN LOS ANTERIORES')
        ],
        string='Catálogo estados financieros',
        default='09',
        required=True
    )
    eeff_presentation_opportunity = fields.Selection(
        selection=[
            ('01', 'Al 31 de diciembre'),
            ('02', 'Al 31 de enero, por modificación del porcentaje'),
            ('03', 'Al 30 de junio, por modificación del coeficiente o porcentaje'),
            ('04',
             'Al último día del mes que sustentará la suspensión o modificación del coeficiente (distinto al 31 de enero o 30 de junio)'),
            ('05',
             'Al día anterior a la entrada en vigencia de la fusión, escisión y demás formas de reorganización de sociedades o emperesas o extinción '
             'de la persona jurídica'),
            ('06', 'A la fecha del balance de liquidación, cierre o cese definitivo del deudor tributario'),
            ('07', 'A la fecha de presentación para libre propósito')
        ],
        string='Oportunidad de presentación de EEFF',
        required=True
    )

    txt_filename = fields.Char(string='Filaname .txt')
    txt_binary = fields.Binary(string='Reporte .TXT 3.7')
    pdf_filename = fields.Char(string='Reporte .PDF 3.7')
    pdf_binary = fields.Binary(string='Reporte .PDF 3.7')

    def name_get(self):
        return [(obj.id, '{} - {}'.format(obj.date_start.strftime('%d/%m/%Y'), obj.date_end.strftime('%d/%m/%Y'))) for
                obj in self]

    def action_generate_report(self):
        self.line_ids.unlink()
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
        {ple_report_inv_val_id} as ple_report_inv_val_07_id,
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
        
        WHERE svl.accounting_date<='{date_end}' and svl.accounting_date>='{date_start}'        
        AND svl.company_id = {company_id}
        GROUP BY pp.id,pt.stock_catalog,pt.stock_type,pt.unspsc_code_id,pt.name,
        uu.l10n_pe_edi_measure_unit_code,svl.company_id
        ORDER BY pp.id DESC             
        """.format(
            company_id=int(self.company_id.id),
            date_start=self.date_start,
            date_end=self.date_end,
            accounts=tuple(acc_q),
            ple_report_inv_val_id=self.id,
        )
        try:
            self.env.cr.execute(query)
            values = self.env.cr.dictfetchall()

            for val in values:

                val['product_description'] = val['product_description']['es_PE']
                product = self.env['product.product'].search([('id', '=', val['product_id'])])

                property_cost_method = product.categ_id.property_cost_method
                if property_cost_method == 'standard':
                    pcm = '9'
                elif property_cost_method == 'average':
                    pcm = '1'
                elif property_cost_method == 'fifo':
                    pcm = '2'
                else:
                    pcm = ''
                val.setdefault('property_cost_method', pcm)

                if val['quantity_product_hand']>0:
                    val.setdefault('standard_price', val['total']/val['quantity_product_hand'])
                else:
                    val.setdefault('standard_price',0)
            lines_report = list(values)

            self.env['ple.report.inv.bal.line.07'].create(lines_report)

        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

    def action_generate_excel(self):
        if self.action_generate_report():
            return
        list_data = []
        year, month, day = self.date_end.strftime('%Y/%m/%d').split('/')
        initial_balances = self.capture_initial_balances_id()
        line_ids = self.env['ple.report.inv.bal.line.07'].search([('ple_report_inv_val_07_id', '=', self.id)])
        for obj_line in line_ids:

            values = {
                'period': '%s%s%s' % (year, month, day),
                'stock_catalog': obj_line.stock_catalog,
                'stock_type': obj_line.stock_type,
                'default_code': obj_line.default_code,
                'property_cost_method': obj_line.property_cost_method,
                'code_catalog_used': obj_line.code_catalog_used,
                'unspsc_code_id': '' if obj_line.unspsc_code_id == 0 else obj_line.unspsc_code_id,
                'product_description': obj_line.product_description,
                'product_udm': obj_line.product_udm,
                'quantity_product_hand': round(obj_line.quantity_product_hand, 2),
                'standard_price': round(obj_line.standard_price, 2),
                'total': round(obj_line.total, 2),
                'last_date': obj_line.last_date,
                'product_id': obj_line.product_id,
                'ple_report_inv_val_07_id': self.id
            }
            list_data.append(values)

        if len(initial_balances) > 0:
            for value_initial in initial_balances:
                values = {
                    'period': '%s%s%s' % (year, month, day),
                    'stock_catalog': value_initial['stock_catalog'],
                    'stock_type': value_initial['stock_type'],
                    'default_code': value_initial['default_code'],
                    'property_cost_method': value_initial['property_cost_method'],
                    'code_catalog_used': value_initial['code_catalog_used'],
                    'unspsc_code_id': value_initial['unspsc_code_id'],
                    'product_description': value_initial['product_description'],
                    'product_udm': value_initial['product_udm'],
                    'quantity_product_hand': value_initial['quantity_product_hand'],
                    'standard_price': value_initial['standard_price'],
                    'total': value_initial['total'],
                    'last_date': value_initial['last_date'],
                    'product_id': value_initial['product_id'],
                    'ple_report_inv_val_07_id': self.id                
                }
                self.env['ple.report.inv.bal.line.07'].create(values)
                list_data.append(values)

        self.write({
            'line_final_ids': [(5, 0, 0)],
        })
     
        for ending_balances in list_data:
            self.write({
                'line_final_ids': [
                    (0, 0, {
                        'stock_catalog': ending_balances['stock_catalog'],
                        'stock_type': ending_balances['stock_type'],
                        'default_code': ending_balances['default_code'],
                        'product_id': ending_balances['product_id'],
                        'property_cost_method': ending_balances['property_cost_method'],
                        'code_catalog_used': ending_balances['code_catalog_used'],
                        'unspsc_code_id': ending_balances['unspsc_code_id'],
                        'product_description': ending_balances['product_description'],
                        'product_udm': ending_balances['product_udm'],
                        'quantity_product_hand': ending_balances['quantity_product_hand'],
                        'standard_price': ending_balances['standard_price'],
                        'total': ending_balances['total'],
                        'last_date': ending_balances['last_date'],
                        'ple_report_inv_val_07_id': self.id,
                    }),
                ]
            })

        report_txt = ReportInvBalTxt(self, list_data)
        report_xls = ReportInvBalExcel(self, list_data)

        values_content = report_txt.get_content()
        values_content_xls = report_xls.get_content()

        data = {
            'txt_binary': base64.b64encode(values_content.encode() or '\n'.encode()),
            'txt_filename': report_txt.get_filename(),
            'error_dialog': 'No hay contenido para presentar en el registro de ventas electrónicos de este periodo.' if not values_content else False,
            'xls_binary': base64.b64encode(values_content_xls),
            'xls_filename': report_xls.get_filename(),
            'date_ple': fields.Date.today(),
            'state': 'load'
        }
        self.write(data)

        for rec in self:
            report_name = "ple_inv_and_bal_0307.action_print_status_finance"
            pdf = self.env.ref(report_name)._render_qweb_pdf('ple_inv_and_bal_0307.print_status_finance', self.id)[0]
            rec.pdf_binary = base64.encodebytes(pdf)
            year, month, day = self.date_end.strftime('%Y/%m/%d').split('/')
            rec.pdf_filename = f'Libro_Mercaderias y Productos Terminados_{year}{month}.pdf'

    def action_close(self):
        self.write({'state': 'closed'})

    def action_rollback(self):
        self.write({'state': 'draft'})
        self.write({
            'txt_binary': False,
            'txt_filename': False,
            'xls_binary': False,
            'xls_filename': False,
            'pdf_binary': False,
            'pdf_filename': False,
            'line_final_ids': [(5, 0, 0)],
            'line_initial_ids': [(5, 0, 0)],
            'line_ids': False,
        })


class PleInvBalLines(models.Model):
    _name = 'ple.report.inv.bal.line.07'
    _description = 'Estado de Situación financiera - Líneas'
    period = fields.Char(string="periodo")
    stock_catalog = fields.Char(string='Código de catálogo')
    stock_type = fields.Char(string='Tipo de Existencia')
    default_code = fields.Char(string="Código propio de la existencia")
    code_catalog_used = fields.Char(string="codigo catalogo utilizado")
    unspsc_code_id = fields.Integer(string="UNSPSC Codigo")
    product_id = fields.Char(string='Product_id')
    product_description = fields.Char(string='Descripcion de existencia')
    product_udm = fields.Char(string='product udm')
    quantity_product_hand = fields.Float(string='QPH')
    standard_price = fields.Float(string='Precio standard')
    property_cost_method = fields.Char("Property cost method")
    aml_id = fields.Integer(string='aml valuation')
    total = fields.Float(string='total')
    company_id = fields.Integer(string='Company id')
    last_date = fields.Date(string="Dia del ultimo registro ")

    ple_report_inv_val_07_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.07',
        string='Reporte de Estado de Situación financiera')