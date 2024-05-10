from datetime import datetime
from odoo import fields, models, api
from odoo.osv import expression
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round
import base64
import pytz
import re


class StockProductsValuation(models.Model):
    _name = 'ple.stock.products.valuation.final'
    _description = 'Valuación de productos en stock - Final'
    ple_stock_products_final = fields.Many2one(string='Valuation book final',
                                               comodel_name="ple.permanent.inventory.physical.units")

    product_id = fields.Integer(string="Id Producto")
    product_valuation = fields.Char(string="Producto")
    quantity_product_hand = fields.Float(string="Cantidad a mano")
    udm_product = fields.Char(string="UDM")
    standard_price = fields.Float(string='Costo unitario')
    total_value = fields.Float(
        string='Valor total', compute='_compute_total_value')
    code_exist = fields.Integer(string='Código de existencia')

    def _compute_total_value(self):
        for data in self:
            data.total_value = float_round(
                data.quantity_product_hand * data.standard_price, 2)


class PlePermanentFinal(models.Model):
    _inherit = 'ple.permanent.inventory.physical.units'

    list_val_unit_final = fields.One2many(
        string="Saldo Final",
        comodel_name="ple.stock.products.valuation.final",
        inverse_name="ple_stock_products_final"
    )

    status_balance_final = fields.Selection([
        ('draft_perm', 'Draft'),
        ('load_perm', 'Open')],
        string='status balanace final', default='draft_perm', readonly=True)

    @api.model
    def update_queries_functions_permanent(self):
        query_functions = """
            CREATE or REPLACE FUNCTION get_number_document(stock_id INT)
            RETURNS VARCHAR
            language plpgsql
            as
            $$
            DECLARE
                new_value VARCHAR;
            BEGIN
                IF (SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'stock_landed_cost')) = true THEN
                    new_value :=COALESCE((
                        SELECT landed_lion.code as new_value
                        FROM stock_landed_cost as landed
                        LEFT JOIN account_move as landed_account          ON      landed.vendor_bill_id=landed_account.id
                        LEFT JOIN l10n_latam_document_type landed_lion    ON      landed_account.l10n_latam_document_type_id=landed_lion.id
                        WHERE landed.id = (SELECT stock_landed_cost_id FROM stock_valuation_layer WHERE id = stock_id)),null);
                ELSE
                    new_value := NULL ;
                END IF;
            RETURN new_value;
            END;
            $$;
            --
            --
            CREATE or REPLACE FUNCTION get_serie_document(stock_id INT)
            RETURNS VARCHAR
            language plpgsql
            as
            $$
            DECLARE
                new_value VARCHAR;
            BEGIN
                IF (SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'stock_landed_cost')) = true THEN
                    new_value :=COALESCE((
                        SELECT SPLIT_PART(landed_account.ref,'-',1)
                        FROM stock_landed_cost as landed
                        LEFT JOIN account_move as landed_account          ON      landed.vendor_bill_id=landed_account.id
                        LEFT JOIN l10n_latam_document_type landed_lion    ON      landed_account.l10n_latam_document_type_id=landed_lion.id
                        WHERE landed.id = (SELECT stock_landed_cost_id FROM stock_valuation_layer WHERE id = stock_id)),null); 
                ELSE
                    new_value := NULL;
                END IF;
            RETURN new_value;
            END;
            $$;
            --
            --
            CREATE or REPLACE FUNCTION get_number_transfer_document(stock_id INT)
            RETURNS VARCHAR
            language plpgsql
            as
            $$
            DECLARE
                new_value VARCHAR;
            BEGIN
                IF (SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'stock_landed_cost')) = true THEN
                    new_value :=COALESCE((
                        SELECT SPLIT_PART(landed_account.ref,'-',2)
                        FROM stock_landed_cost as landed                 
                        LEFT JOIN account_move as landed_account          ON      landed.vendor_bill_id=landed_account.id
                        LEFT JOIN l10n_latam_document_type landed_lion    ON      landed_account.l10n_latam_document_type_id=landed_lion.id
                        WHERE landed.id=(SELECT stock_landed_cost_id FROM stock_valuation_layer WHERE id = stock_id)),null);
                ELSE
                    new_value := NULL;
                END IF;
            RETURN new_value;
            END;
            $$;
            """
        self.env.cr.execute(query_functions)

    def action_generate_data(self):
        start_date = '%s 00:00:00' % self.date_start
        finish_date = '%s 23:59:59' % self.date_end

        query = """
            SELECT 
                stock_valuation_layer.id as stock_valuation,
                product_product.id as product_id,
                TO_CHAR(coalesce(account_move.date,stock_valuation_layer.accounting_date),'YYYYMM00') as period,
                CONCAT(replace(account_move.name, '/', ''), stock_valuation_layer.id) as cou,
                coalesce(
                (
                SELECT 
                    coalesce(account_move_line.ple_correlative, 'M000000001')
                FROM account_move       
                LEFT JOIN account_move_line ON account_move.id = account_move_line.move_id
                LEFT JOIN account_account   ON account_move_line.account_id = account_account.id
                WHERE (account_move_line.product_id=product_product.id)  AND ("account_move"."id" = stock_valuation_layer.account_move_id) 
                AND (LEFT(account_account.code,2)='20') LIMIT 1
                ), 'M000000001') as correlativo, 
                coalesce(res_partner.annexed_establishment,
                coalesce(CASE WHEN stock_location.usage = 'internal' THEN res_partner_orig.annexed_establishment 
                ELSE 
                (CASE WHEN stock_location_dest.usage = 'internal' THEN res_partner_dest.annexed_establishment ELSE stock_establishment.annexed_establishment END
                )END, '')
                ) as establishment,
                coalesce(product_template.stock_catalog,'') as catalog ,
                coalesce(product_template.stock_type,'') as stock_type,
                coalesce(LEFT(replace(replace(replace(product_product.default_code, '_', ''), '-', ''), ' ', ''),24),'') as default_code,
                coalesce(CASE WHEN product_template.unspsc_code_id > 0 THEN '1' ELSE '' END,'') as code_catag,
                coalesce(product_unspsc_code.code,'') as unspsc_code,
                TO_CHAR(coalesce(account_move.date,stock_valuation_layer.accounting_date),'DD/MM/YYYY') as date_start,
                
                CASE WHEN stock_picking.picking_number != '' THEN '09'
                ELSE                 
                COALESCE(l10n_latam_document_type.code, '00')
                END as number_document,
                
                CASE WHEN stock_picking.picking_number != '' THEN 
                LEFT(stock_picking.picking_number, 4)
                ELSE                 
                COALESCE(REGEXP_REPLACE(stock_picking.serie_transfer_document, '[^a-zA-Z0-9]', '', 'g'), '0')
                END as serie_document,
                
                CASE WHEN stock_picking.picking_number != '' 
                THEN SPLIT_PART(stock_picking.picking_number, '-', 2)
                ELSE 
                                
                COALESCE(REGEXP_REPLACE(stock_picking.number_transfer_document, '[^a-zA-Z0-9]', '', 'g'), '0')
                END as reference_document,    
                
                CASE WHEN  stock_valuation_layer.sunat_operation_type is not null then
                stock_valuation_layer.sunat_operation_type
                WHEN stock_move.picking_id > 0 then              
                coalesce (coalesce(stock_picking.type_operation_sunat,'99'),stock_picking_type.ple_reason_id)
                WHEN stock_picking.origin LIKE '%retorno%' THEN
                coalesce (stock_picking_type.code,stock_picking_type.ple_revert_id)
                ELSE  
                coalesce((CASE WHEN stock_move.location_id > 0
                then (case when stock_location_dest.usage = 'inventory' then '28' ELSE '99' end)
                ELSE '99' END ), '99')
                END as type_operation,
    
                --coalesce(LEFT(pol.name,80), LEFT(product_template.name,80)) as description_prod,
                --coalesce(LEFT(pol.name,80), LEFT(product_template.name,80)) as description,
    
                LEFT(uom_uom.l10n_pe_edi_measure_unit_code,3) as uom,
                uom_uom.name as uom_name,
    
                coalesce(CASE WHEN stock_valuation_layer.quantity > 0 THEN stock_valuation_layer.quantity
                ELSE'0.00' END,'0.00') as quantity_product_hand,
                coalesce(CASE WHEN stock_valuation_layer.unit_cost > 0 THEN stock_valuation_layer.unit_cost
                ELSE '0.00' END,'0.00') as standard_price,
                coalesce(CASE WHEN stock_valuation_layer.value > 0 THEN stock_valuation_layer.value
                ELSE '0.00' END,'0.00') as total_value,
                coalesce(CASE WHEN stock_valuation_layer.quantity < 0 THEN stock_valuation_layer.quantity
                ELSE'0.00' END,'0.00') as quantity,
                coalesce(CASE WHEN stock_valuation_layer.unit_cost < 0 THEN stock_valuation_layer.unit_cost
                ELSE '0.00' END,'0.00') as unit_cost,
                coalesce(CASE WHEN stock_valuation_layer.value < 0 THEN stock_valuation_layer.value
                ELSE '0.00' END,'0.00') as value_cost
    
            FROM stock_valuation_layer
                LEFT JOIN account_move           ON     stock_valuation_layer.account_move_id = account_move.id
                LEFT JOIN stock_move             ON     stock_valuation_layer.stock_move_id = stock_move.id
                LEFT JOIN stock_warehouse        ON     stock_move.warehouse_id = stock_warehouse.id
                LEFT JOIN res_partner            ON     stock_warehouse.partner_id = res_partner.id
                LEFT JOIN stock_location         ON     stock_move.location_id = stock_location.id
                LEFT JOIN stock_warehouse as stock_warehouse_orig  ON     stock_location.storehouse_id  = stock_warehouse_orig.id
                LEFT JOIN res_partner as res_partner_orig          ON     stock_warehouse_orig.partner_id = res_partner_orig.id
    
                LEFT JOIN stock_picking          ON     stock_move.picking_id = stock_picking.id
                LEFT JOIN stock_picking_type     ON     stock_picking.picking_type_id = stock_picking_type.id
                LEFT JOIN product_product        ON     stock_valuation_layer.product_id = product_product.id
                LEFT JOIN product_template       ON     product_product.product_tmpl_id = product_template.id
                LEFT JOIN product_category       ON     product_template.categ_id = product_category.id
                LEFT JOIN uom_uom                ON     product_template.uom_id = uom_uom.id
                LEFT JOIN product_unspsc_code    ON     product_template.unspsc_code_id = product_unspsc_code.id
                LEFT JOIN l10n_latam_document_type ON    stock_picking.transfer_document_type_id=l10n_latam_document_type.id
    
                LEFT JOIN stock_location as stock_location_dest   ON     stock_move.location_dest_id = stock_location_dest.id
                LEFT JOIN stock_warehouse as stock_warehouse_dest ON     stock_location_dest.storehouse_id  = stock_warehouse_dest.id
                LEFT JOIN res_partner as res_partner_dest         ON     stock_warehouse_dest.partner_id = res_partner_dest.id
    
                LEFT JOIN res_company           ON      stock_valuation_layer.company_id=res_company.id
                LEFT JOIN res_partner as stock_establishment      ON      res_company.partner_id=stock_establishment.id
                --LEFT JOIN purchase_order_line  pol      ON      pol.id = stock_move.purchase_line_id
    
            WHERE ("stock_valuation_layer"."accounting_date" >= '{start_date}') AND 
                ("stock_valuation_layer"."accounting_date"<='{end_date}') AND ("product_template"."type" = 'product')
                AND (stock_valuation_layer.company_id = '{company_id}')
                ORDER BY product_id DESC,"stock_valuation_layer"."create_date" ASC ,stock_valuation DESC;
            """.format(
            start_date=start_date,
            end_date=finish_date,
            company_id=self.company_id.id,
        )

        try:
            self.env.cr.execute(query)
            data_aml = self.env.cr.dictfetchall()
            return data_aml
        except Exception as error:
            raise ValidationError(
                f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

    def calculate_products_final(self):
        balance_ending = self.generete_ending_balances()
        self.write({
            'list_val_unit_final': [(5, 0, 0)],
        })
        for rec in balance_ending.keys():
            res = balance_ending.get(rec)
            self.write({
                'list_val_unit_final': [
                    (0, 0, {'product_id': rec,
                            'product_valuation': res['product_valuation'],
                            'quantity_product_hand': res['quantity_product_hand'],
                            'udm_product': res['udm_product'],
                            'standard_price': res['standard_price'],
                            'code_exist': res['code_exist'],
                            }),
                ]
            })

    def generete_ending_balances(self):
        data_aml = self.action_generate_data()
        hand_accumulated = 0
        total_accumulated = 0
        product_id = 0
        start_date = self.date_start
        year, month, day = start_date.strftime('%Y/%m/%d').split('/')
        opening_balances = self.opening_balances_id()
        ending_balances = dict()
        open_balance = list()
        quantity_hand = dict()

        for datos in self.list_val_units:
            open_balance.append(datos.product_id)
            quantity_hand[datos.product_id] = {}
            quantity_hand[datos.product_id]['quantity_product_hand'] = datos.quantity_product_hand
            quantity_hand[datos.product_id]['product_valuation'] = datos.product_valuation
            quantity_hand[datos.product_id]['udm_product'] = datos.udm_product
            quantity_hand[datos.product_id]['standard_price'] = datos.standard_price
            quantity_hand[datos.product_id]['total_value'] = datos.total_value
            quantity_hand[datos.product_id]['code_exist'] = datos.code_exist

        env = self.env['product.product']
        for obj_move_line in data_aml:
            product = env.browse(obj_move_line.get('product_id'))
            display_name = product.display_name.split(']')[-1].strip()[:80]
            if obj_move_line.get('product_id') != product_id:

                if product_id != 0:
                    if product_id in open_balance:
                        open_balance.remove(product_id)
                    if hand_accumulated != 0:
                        ending_balances[product_id] = {}
                        ending_balances[product_id]['product_valuation'] = product_valuation_final
                        ending_balances[product_id]['quantity_product_hand'] = hand_accumulated
                        ending_balances[product_id]['udm_product'] = udm_product_final
                        ending_balances[product_id]['standard_price'] = standar_price_final
                        ending_balances[product_id]['code_exist'] = code_final
                hand_accumulated = 0
                total_accumulated = 0
                ids = obj_move_line.get('product_id')

                if ids in opening_balances:
                    datos = self.opening_balances(ids, quantity_hand.get(ids), year, month, day, correct_name=display_name)
                    hand_accumulated = datos['quantity_hand_accumulated']
                    total_accumulated = datos['cost_total_accumulated']
                    opening_balances.remove(ids)

            total_hand = obj_move_line.get('quantity_product_hand', '') + obj_move_line.get('quantity', '0') + hand_accumulated
            total_total = obj_move_line.get('total_value', '') + obj_move_line.get('value_cost', '0') + total_accumulated
            
            if round(total_hand, 2) == 0:
                divisor = 1
            else:
                divisor = total_hand

            property_cost_method = product.categ_id.property_cost_method
            code = ''
            if property_cost_method == 'standard':
                code = '9'
            elif property_cost_method == 'average':
                code = '1'
            elif property_cost_method == 'fifo':
                code = '2'

            product_valuation_final = display_name
            udm_product_final = obj_move_line.get('uom', '')
            standar_price_final = total_total / divisor
            code_final = code

            product_id = obj_move_line.get('product_id')
            hand_accumulated = total_hand
            total_accumulated = total_total

        if data_aml:
            if product_id in open_balance:
                open_balance.remove(product_id)

            if hand_accumulated != 0:
                ending_balances[product_id] = {}
                ending_balances[product_id]['product_valuation'] = product_valuation_final
                ending_balances[product_id]['quantity_product_hand'] = hand_accumulated
                ending_balances[product_id]['udm_product'] = udm_product_final
                ending_balances[product_id]['standard_price'] = standar_price_final
                ending_balances[product_id]['code_exist'] = code_final

        if open_balance:
            for rec in open_balance:
                product_id = rec
                datos = quantity_hand.get(product_id)
                ending_balances[product_id] = {}
                ending_balances[product_id]['product_valuation'] = datos['product_valuation']
                ending_balances[product_id]['quantity_product_hand'] = datos['quantity_product_hand']
                ending_balances[product_id]['udm_product'] = datos['udm_product']
                ending_balances[product_id]['standard_price'] = datos['standard_price']
                ending_balances[product_id]['code_exist'] = datos['code_exist']

        return ending_balances

    def opening_balances_id(self):
        products_id = []
        for datos in self.list_val_units:
            products_id.append(datos.product_id)

        return products_id

    def opening_balances(self, product, quantity_hand, year, month, day, correct_name=False):
        product_product = self.env['product.product'].search(
            [('id', '=', product)])

        related_stock_valuation_layer = self.env['stock.valuation.layer'].search([('product_id', '=', product)], order='id asc', limit=1)

        if round(quantity_hand['quantity_product_hand'], 2) == 0:
            divisor = 1
        else:
            divisor = quantity_hand['quantity_product_hand']

        if product_product.unspsc_code_id.id > 0:
            code_catag = '1'
        else:
            code_catag = ''

        if not correct_name:
            correct_name = product_product.display_name.split(
                ']')[-1].strip()[:80]
        datos = {
            'period': '%s%s00' % (year, month),
            'cou': 'SALDOINICIAL%s%s%s%s' % (year, month, product, str(related_stock_valuation_layer.id)),
            'correlativo': 'M000000001',
            'establishment': self.company_id.partner_id.annexed_establishment,
            'catalog': product_product.stock_catalog if product_product.stock_catalog else '',
            'stock_type': product_product.stock_type if product_product.stock_type else '',
            'default_code': re.sub('[^A-Za-z0-9]+', '',
                                   product_product.default_code if product_product.default_code else ''),
            'code_catag': code_catag,
            'unspsc_code': product_product.unspsc_code_id.code if product_product.unspsc_code_id.code else '',
            'date_start': '%s/%s/%s' % (day, month, year),
            'number_document': '00',
            'serie_document': '0',
            'reference_document': '0',
            'type_operation': '16',
            'description_prod': correct_name,
            'description': correct_name,
            'uom': quantity_hand['udm_product'],
            'code_exist': quantity_hand['code_exist'],
            'quantity_product_hand': quantity_hand['quantity_product_hand'],
            'standard_price': quantity_hand['standard_price'],
            'total_value': quantity_hand['total_value'],
            'quantity': 0.00,
            'unit_cost': 0.00,
            'value_cost': 0.00,
            'quantity_hand_accumulated': round(quantity_hand['quantity_product_hand'], 2),
            'cost_unit_accumulated': round(quantity_hand['total_value'] / divisor, 2),
            'cost_total_accumulated': round(quantity_hand['total_value'], 2),
            'state': '1',
            'header': True,
        }
        return datos
