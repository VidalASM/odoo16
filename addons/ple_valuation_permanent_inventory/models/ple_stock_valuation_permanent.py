import base64
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from ..reports.report_valuation_inventory import LedgerReportExcel, LedgerReportTxt


class PleValuationPermanent(models.Model):
    _inherit = 'ple.permanent.inventory.physical.units'

    xls_filename_valued = fields.Char(string='Filaname Excel')
    xls_binary_valued = fields.Binary(string='Reporte Excel valorizado')
    txt_filename_valued = fields.Char(string='Filaname .TXT')
    txt_binary_valued = fields.Binary(string='Reporte .TXT valorizado')

    status_permanent = fields.Selection([
        ('draft_perm', 'Draft'),
        ('load_perm', 'Open'),
        ('closed_perm', 'Cancelled')
    ], string='status permanent', default='draft_perm', readonly=True)

    def action_generate_report_valued(self):
        data_aml = self.action_generate_data()
        list_data = []
        hand_accumulated = 0
        total_accumulated = 0
        product_id = 0
        value_1 = 0.00
        value_2 = 0.00
        list_data_non = []

        start_date = self.date_start
        year, month, day = start_date.strftime('%Y/%m/%d').split('/')
        opening_balances = self.opening_balances_id()

        quantity_hand = dict()
        for datos in self.list_val_units:
            quantity_hand[datos.product_id] = {}
            quantity_hand[datos.product_id]['quantity_product_hand'] = datos.quantity_product_hand
            quantity_hand[datos.product_id]['udm_product'] = datos.udm_product
            quantity_hand[datos.product_id]['standard_price'] = datos.standard_price
            quantity_hand[datos.product_id]['total_value'] = datos.total_value
            quantity_hand[datos.product_id]['code_exist'] = datos.code_exist

        env = self.env['product.product']
        for obj_move_line in data_aml:
            header = True
            product = env.browse(obj_move_line.get('product_id'))
            display_name = product.display_name.split(']')[-1].strip()[:80]
            if obj_move_line.get('product_id') != product_id:
                hand_accumulated = 0
                total_accumulated = 0
                ids = obj_move_line.get('product_id')
                list_data_non.append(ids)
                if ids in opening_balances:
                    datos = self.opening_balances(ids, quantity_hand.get(ids), year, month, day, correct_name=display_name)

                    list_data.append(datos)
                    header = False
                    hand_accumulated = datos['quantity_hand_accumulated']
                    total_accumulated = datos['cost_total_accumulated']
                    opening_balances.remove(ids)

            else:
                header = False

            total_hand = obj_move_line.get('quantity_product_hand', '') + obj_move_line.get('quantity',
                                                                                            '0') + hand_accumulated
            total_total = obj_move_line.get('total_value', '') + obj_move_line.get('value_cost',
                                                                                   '0') + total_accumulated
            if round(total_hand, 2) == 0:
                divisor = 1
                total_total = 0
            else:
                divisor = total_hand

            if obj_move_line.get('total_value', '') > 0.00:
                value_1 = obj_move_line.get('standard_price', '')
                value_2 = 0.00
            else:
                value_1 = 0.00
                value_2 = obj_move_line.get('standard_price', '')

            property_cost_method = product.categ_id.property_cost_method
            code = ''
            if property_cost_method == 'standard':
                code = '9'
            elif property_cost_method == 'average':
                code = '1'
            elif property_cost_method == 'fifo':
                code = '2'

            values = {
                'period': '%s%s00' % (year, month),
                'cou': obj_move_line.get('cou', ''),
                'correlativo': obj_move_line.get('correlativo', ''),
                'establishment': obj_move_line.get('establishment', ''),
                'catalog': obj_move_line.get('catalog', ''),
                'stock_type': obj_move_line.get('stock_type', ''),
                'default_code': obj_move_line.get('default_code', ''),
                'code_catag': obj_move_line.get('code_catag', ''),
                'unspsc_code': obj_move_line.get('unspsc_code', ''),
                'date_start': obj_move_line.get('date_start', ''),
                'number_document': obj_move_line.get('number_document', '00'),
                'serie_document': ''.join(filter(str.isalnum, obj_move_line.get('serie_document', '0')))[:20],
                'reference_document': (''.join(
                    filter(str.isalnum, obj_move_line.get('reference_document', '0')))).zfill(8)[:20],
                'type_operation': obj_move_line.get('type_operation', ''),
                'description_prod': display_name,
                'description': display_name,
                'uom': obj_move_line.get('uom', ''),
                'code_exist': code,
                'quantity_product_hand': obj_move_line.get('quantity_product_hand', ''),
                'standard_price': value_1,
                'total_value': obj_move_line.get('total_value', ''),
                'quantity': obj_move_line.get('quantity', ''),
                'unit_cost': value_2,
                'value_cost': obj_move_line.get('value_cost', ''),
                'quantity_hand_accumulated': round(total_hand, 2),
                'cost_unit_accumulated': round((total_total / divisor), 2),
                'cost_total_accumulated': round(total_total, 2),
                'state': '1',
                'header': header,
            }
            product_id = obj_move_line.get('product_id')
            hand_accumulated = total_hand
            total_accumulated = total_total
            list_data.append(values)

        for datos_non in opening_balances:
            datos = self.opening_balances(datos_non, quantity_hand.get(datos_non), year, month, day, correct_name=False)
            list_data.append(datos)

        ledger_report_xls = LedgerReportExcel(self, list_data)
        ledger_content_xls = ledger_report_xls.get_content()
        ledger_report = LedgerReportTxt(self, list_data)
        ledger_content = ledger_report.get_content()

        data = {
            'xls_binary_valued': base64.b64encode(ledger_content_xls),
            'xls_filename_valued': ledger_report_xls.get_filename(),
            'txt_binary_valued': base64.b64encode(ledger_content and ledger_content.encode() or '\n'.encode()),
            'txt_filename_valued': ledger_report.get_filename(),
            'status_permanent': 'load_perm'
        }
        self.write(data)
        return True

    def action_rollback_permanent(self):
        self.write({
            'xls_binary_valued': False,
            'xls_filename_valued': False,
            'txt_binary_valued': False,
            'txt_filename_valued': False,
            'status_permanent': 'draft_perm',
        })
