from datetime import datetime
from odoo import fields, models, api
from odoo.osv import expression
from ..reports.report_permanent_inventory_physical_units import PermanentInventoryPhysicalUnitsReport
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round
import base64
import pytz


class PlePermanentInventoryPhysicalUnits(models.Model):
    _name = 'ple.permanent.inventory.physical.units'
    _description = 'Inventario Permanente en Unidades físicas'
    _inherit = 'ple.report.base'
    validation_calc_balance = fields.Boolean(string="Booleano")
    validation_generate_report = fields.Boolean(string="Booleano")

    list_val_units = fields.One2many(
        string="Saldo Inicial",
        comodel_name="ple.stock.products.valuation",
        inverse_name="ple_stock_products"
    )

    @api.depends('date_start')
    def action_calc_balance(self):
        self.validation_calc_balance = True
        start_date = self.date_start
        finish_date = datetime(
            start_date.year, start_date.month, start_date.day)
        datos = self.action_generate_product_list(finish_date)
        self.write({
            'list_val_units': [(5, 0, 0)]
        })
        for rec in datos.keys():
            res = datos.get(rec)
            if res['quantity_product_hand'] != 0.00:
                self.write({
                    'list_val_units': [
                        (0, 0, {'product_id': rec,
                                'product_valuation': res['product_valuation'],
                                'quantity_product_hand': res['quantity_product_hand'],
                                'udm_product': res['udm_product'],
                                'standard_price': res['standard_price'],
                                'code_exist': res['code_exist'],
                                }),
                    ]
                })

    def action_generate_product_list(self, to_date):
        product = self.env['product.product'].search(
            [('type', '=', 'product')])
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product._get_domain_locations()
        domain_quant = [('product_id', 'in', product.ids)] + domain_quant_loc
        dates_in_the_past = False
        to_date = fields.Datetime.to_datetime(to_date)
        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', product.ids)
                          ] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', product.ids)
                           ] + domain_move_out_loc

        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if to_date:
            date_date_expected_domain_to = [('date', '<=', to_date)]
            domain_move_in += date_date_expected_domain_to
            domain_move_out += date_date_expected_domain_to

        Move = self.env['stock.move'].with_context(active_test=False)
        Quant = self.env['stock.quant'].with_context(active_test=False)
        domain_move_in_todo = [('state', 'in',
                                ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
        domain_move_out_todo = [('state', 'in',
                                 ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in
                            Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'],
                                            orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in
                             Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'],
                                             orderby='id'))
        quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'])) for item in
                          Quant.read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity'],
                                           ['product_id'], orderby='id'))
        if dates_in_the_past:
            domain_move_in_done = [
                ('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [
                ('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                     Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'],
                                                     orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                      Move.read_group(domain_move_out_done, ['product_id', 'product_qty'],
                                                      ['product_id'], orderby='id'))

        res = dict()
        for product in product.with_context(prefetch_fields=False):
            product_id = product.id
            if not product_id:
                res[product_id] = dict.fromkeys(
                    ['product_valuation', 'quantity_product_hand', 'udm_product', 'standard_price', 'total_value',
                     'code_exist'],
                    0.0,
                )
                continue
            rounding = product.uom_id.rounding
            res[product_id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(product_id, [0.0])[0] - moves_in_res_past.get(product_id,
                                                                                             0.0) + moves_out_res_past.get(
                    product_id, 0.0)
            else:
                qty_available = quants_res.get(product_id, [0.0])[0]

            code = ''
            property_cost_method = product.categ_id.property_cost_method
            if property_cost_method == 'standard':
                code = '9'
            elif property_cost_method == 'average':
                code = '1'
            elif property_cost_method == 'fifo':
                code = '2'

            res[product_id]['product_valuation'] = product.name
            res[product_id]['quantity_product_hand'] = float_round(
                qty_available, precision_rounding=rounding)
            res[product_id]['udm_product'] = product.uom_id.l10n_pe_edi_measure_unit_code
            res[product_id]['standard_price'] = float_round(
                product.standard_price, precision_rounding=rounding)
            res[product_id]['code_exist'] = code

        return res

    def action_generate_excel(self):
        start_date = '%s 00:00:00' % self.date_start
        finish_date = '%s 23:59:59' % self.date_end

        query = """
                SELECT 

                TO_CHAR(coalesce(am.date,svl.accounting_date),'YYYYMM00') as period_name,
                CONCAT(replace(am.name, '/', ''), svl.id) as cou,
                pp.id as product_id,
                svl.id as stock_valuation,
                COALESCE(
                    (
                        SELECT aml.ple_correlative AS correlative
                        FROM account_move am
                        LEFT JOIN account_move_line aml ON am.id = aml.move_id
                        LEFT JOIN account_account aa ON aml.account_id = aa.id
                        WHERE (am.id = svl.account_move_id) AND aa.ple_selection = 'stock_revaluation_book'
                        LIMIT 1
                    ),
                    'M000000001'
                ) AS correlative,
                COALESCE(rp.annexed_establishment,
                COALESCE(CASE WHEN sl.usage = 'internal' THEN rpo.annexed_establishment 
                ELSE 
                (CASE WHEN sld.usage = 'internal' THEN rpd.annexed_establishment ELSE '' END)
                END, '')
                ) as establishment,

                --COALESCE(LEFT(pol.name,80), COALESCE(LEFT(pt.name,80), '')) as  description,
                --COALESCE(LEFT(pol.name,80), COALESCE(LEFT(pt.name,80), '')) as correct_name,
                COALESCE(pt.stock_type, '') as stock_type,
                COALESCE(pt.stock_catalog, '') as stock_catalog,
                COALESCE(LEFT(REPLACE(REPLACE(REPLACE(pp.default_code, '_', ''), '-', ''), ' ', ''),24),'')  as stock_own_code,
                COALESCE(CASE WHEN pt.unspsc_code_id>0 THEN '1' ELSE '' END,'') as stock_code,
                COALESCE(puc.code,'') as unspsc_code,
                LEFT(uu.l10n_pe_edi_measure_unit_code,3) as unit_measure_code,
                uu.name as uom_name,
                TO_CHAR(COALESCE(am.date,svl.accounting_date),'dd/mm/YYYY') as date_start,

                CASE WHEN sp.picking_number != '' THEN '09'
                ELSE 
                COALESCE(lldt.code, '00')
                END as document_type,

                CASE WHEN sp.picking_number != '' THEN LEFT(sp.picking_number, 4)
                ELSE 
                COALESCE(REGEXP_REPLACE(sp.serie_transfer_document, '[^a-zA-Z0-9]', '', 'g'), '0')
                END as serie_document,

                CASE WHEN sp.picking_number != '' THEN SPLIT_PART(sp.picking_number, '-', LENGTH(sp.picking_number) - LENGTH(REPLACE(sp.picking_number, '-', '')))

                ELSE 
                COALESCE(REGEXP_REPLACE(sp.number_transfer_document, '[^a-zA-Z0-9]', '', 'g'), '0')
                END as number_document,
                
                CASE WHEN svl.sunat_operation_type is not null then
                svl.sunat_operation_type
                WHEN sm.picking_id > 0 then              
                coalesce (coalesce(sp.type_operation_sunat,'99'),spt.ple_reason_id)
                WHEN sp.origin LIKE '%retorno%' THEN
                coalesce (spt.code,spt.ple_revert_id)
                ELSE  
                coalesce((CASE WHEN sm.location_id > 0
                then (case when sl.usage = 'inventory' then '28' ELSE '99' end)
                ELSE '99' END ), '99')
                END as operation_type,

                Coalesce(CASE WHEN svl.quantity > 0 THEN svl.quantity
                ELSE'0.00' END,'0.00') as quantity_product_hand,
                coalesce(CASE WHEN svl.quantity < 0 THEN svl.quantity
                ELSE'0.00' END,'0.00') as quantity


                FROM stock_valuation_layer svl
                LEFT JOIN account_move     		am    	ON		svl.account_move_id=am.id
                LEFT JOIN stock_move			sm		ON	 	svl.stock_move_id=sm.id
                LEFT JOIN stock_warehouse       sw      ON      sm.warehouse_id = sw.id
                LEFT JOIN res_partner           rp      ON     sw.partner_id = rp.id
                LEFT JOIN stock_location		sl		ON		sl.id=sm.location_id
                LEFT JOIN stock_warehouse       swo     ON      sl.storehouse_id = swo.id
                LEFT JOIN res_partner           rpo     ON      swo.partner_id = rpo.id

                LEFT JOIN stock_picking       sp        ON     sm.picking_id = sp.id
                LEFT JOIN stock_picking_type   spt      ON     sp.picking_type_id = spt.id
                LEFT JOIN product_product       pp      ON     svl.product_id = pp.id
                LEFT JOIN product_template      pt      ON     pp.product_tmpl_id = pt.id
                LEFT JOIN product_category      pc      ON     pt.categ_id = pc.id
                LEFT JOIN uom_uom              uu       ON     pt.uom_id = uu.id
                LEFT JOIN product_unspsc_code  puc      ON     pt.unspsc_code_id = puc.id
                LEFT JOIN l10n_latam_document_type  lldt ON   sp.transfer_document_type_id=lldt.id
            

                LEFT JOIN stock_location       sld      ON      sm.location_dest_id = sld.id
                LEFT JOIN stock_warehouse      swd      ON      sld.storehouse_id = swd.id
                LEFT JOIN res_partner          rpd      ON      swd.partner_id = rpd.id
                --LEFT JOIN purchase_order_line  pol      ON      pol.id = sm.purchase_line_id

                WHERE 
                (svl.accounting_date BETWEEN '{date_start}' and '{date_end}') and
                (pt.type = 'product') and (svl.quantity !=0) and (svl.company_id='{company}')
                ORDER BY
                product_id DESC,
                svl.create_date ASC, 
                stock_valuation DESC;

                """.format(
            date_start=start_date,
            company=self.company_id.id,
            date_end=finish_date,
        )

        try:
            self.env.cr.execute(query)
            data_aml = self.env.cr.dictfetchall()
            return data_aml
        except Exception as error:
            raise ValidationError(
                f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

    def action_generate_report(self):
        self.validation_generate_report = True
        data_aml = self.action_generate_excel()
        product_id = 0
        list_data = []
        list_data_non = []

        start_date = self.date_start
        year, month, day = start_date.strftime('%Y/%m/%d').split('/')
        opening_balances_unit = self.opening_balance_id_units()
        quantity_hand = dict()

        for datos in self.list_val_units:
            quantity_hand[datos.product_id] = {}
            quantity_hand[datos.product_id]['quantity_product_hand'] = datos.quantity_product_hand
            quantity_hand[datos.product_id]['udm_product'] = datos.udm_product

        env = self.env['product.product']
        for obj_move_line in data_aml:
            header = True
            display_name = env.browse(obj_move_line.get(
                'product_id')).display_name.split(']')[-1].strip()[:80]
            if obj_move_line.get('product_id') != product_id:
                ids = obj_move_line.get('product_id')
                list_data_non.append(ids)
                if ids in opening_balances_unit:
                    datos = self.opening_balance_units(ids, quantity_hand.get(ids), year, month, day,
                                                       correct_name=display_name)
                    list_data.append(datos)
                    header = False
                    opening_balances_unit.remove(ids)
            else:
                header = False

            values = {
                'period': '%s%s00' % (year, month),
                'cuo': obj_move_line.get('cou', ''),
                'correlative': obj_move_line.get('correlative', ''),
                'annexed_establishment_code': obj_move_line.get('establishment', ''),
                'stock_catalog': obj_move_line.get('stock_catalog', ''),
                'stock_type': obj_move_line.get('stock_type', ''),
                'stock_own_code': obj_move_line.get('stock_own_code', ''),
                'catalog_code': obj_move_line.get('stock_code', ''),
                'stock_code': obj_move_line.get('unspsc_code', ''),
                'valuation_date': obj_move_line.get('date_start', ''),
                'document_type': obj_move_line.get('document_type', ''),
                'series': ''.join(filter(str.isalnum, obj_move_line.get('serie_document', '0')))[:20],
                'document_number': (''.join(filter(str.isalnum, obj_move_line.get('number_document', '0')))).zfill(8)[
                    :20],
                'operation_type': obj_move_line.get('operation_type', ''),
                'stock_description': display_name,
                'description': display_name,
                'unit_measure_code': obj_move_line.get('unit_measure_code', ''),
                'qty_physical_units_asset_entered': obj_move_line.get('quantity_product_hand', ''),
                'qty_physical_units_asset_removed': obj_move_line.get('quantity', '0'),
                'state': '1',
                'header': header,
            }

            product_id = obj_move_line.get('product_id')
            list_data.append(values)

        for datos_non in opening_balances_unit:
            datos = self.opening_balance_units(
                datos_non, quantity_hand.get(datos_non), year, month, day)
            list_data.append(datos)

        report = PermanentInventoryPhysicalUnitsReport(self, list_data)
        content_txt = report.get_content_txt()
        content_xls = report.get_content_excel()

        data = {
            'txt_binary': base64.b64encode(content_txt and content_txt.encode() or '\n'.encode()),
            'txt_filename': report.get_filename(file_type='txt'),
            'xls_binary': base64.b64encode(content_xls),
            'xls_filename': report.get_file_excel(file_type='xlsx'),
            'error_dialog': '' if content_txt else '- No hay contenido en el registro.',
            'date_ple': fields.Date.today(),
            'state': 'load'
        }
        self.write(data)
        return True

    def opening_balance_id_units(self):
        products_id = []
        for datos in self.list_val_units:
            products_id.append(datos.product_id)

        return products_id

    def opening_balance_units(self, product, quantity_hand, year, month, day, correct_name=False):
        product_product = self.env['product.product'].search(
            [('id', '=', product)])

        related_stock_valuation_layer = self.env['stock.valuation.layer'].search([('product_id', '=', product)], order='id asc', limit=1)

        if product_product.unspsc_code_id.id > 0:
            code_catag = '1'
        else:
            code_catag = ''

        if not correct_name:
            correct_name = product_product.display_name.split(
                ']')[-1].strip()[:80]
        datos = {
            'period': '%s%s00' % (year, month),
            'cuo': 'SALDOINICIAL%s%s%s%s' % (year, month, product, str(related_stock_valuation_layer.id)),
            'correlative': 'M000000001',
            'annexed_establishment_code': self.company_id.partner_id.annexed_establishment,
            'stock_catalog': product_product.stock_catalog if product_product.stock_catalog else '',
            'stock_type': product_product.stock_type if product_product.stock_type else '',
            'stock_own_code': product_product.default_code if product_product.default_code else '',
            'catalog_code': code_catag,
            'stock_code': product_product.unspsc_code_id.code if product_product.unspsc_code_id.code else '',
            'valuation_date': '%s/%s/%s' % (day, month, year),
            'document_type': '00',
            'series': '0',
            'document_number': '0',
            'operation_type': '16',
            'stock_description': correct_name,
            'description': correct_name,
            'unit_measure_code': quantity_hand['udm_product'],
            'qty_physical_units_asset_entered': quantity_hand['quantity_product_hand'],
            'qty_physical_units_asset_removed': 0.00,
            'state': '1',
            'header': True,
        }
        return datos

    def action_close(self):
        super(PlePermanentInventoryPhysicalUnits, self).action_close()

    def action_rollback(self):
        super(PlePermanentInventoryPhysicalUnits, self).action_rollback()
        self.write({
            'xls_filename': False,
            'xls_binary': False,
            'txt_binary': False,
            'txt_filename': False,
        })
