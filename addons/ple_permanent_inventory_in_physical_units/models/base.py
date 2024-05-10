from odoo import api, models, fields, _
from odoo.tools import float_round

stock_picking_reason = [
    ('01', "[01] Venta Nacional"),
    ('02', "[02] Compra Nacional"),
    ('03', "[03] Consignación Recibida"),
    ('04', "[04] Consignación Entregada"),
    ('05', "[05] Devolución Recibida"),
    ('06', "[06] Devolución Entregada"),
    ('07', "[07] Bonificación"),
    ('08', "[08] Premio"),
    ('09', "[09] Donación"),
    ('10', "[10] Salida a Producción"),
    ('11', "[11] Salida Transferencia entre almacenes"),
    ('12', "[12] Retiro"),
    ('13', "[13] Mermas"),
    ('14', "[14] Desmedros"),
    ('15', "[15] Destrucción"),
    ('16', "[16] Saldo Inicial"),
    ('17', "[17] Exportación"),
    ('18', "[18] Importación"),
    ('19', "[19] Entrada de Producción"),
    ('20', "[20] Entrada devolución de producción"),
    ('21', "[21] Entrada Transferencia entre almacenes"),
    ('22', "[22] Entrada por identificación erronea"),
    ('23', "[23] Salida por identificación erronea"),
    ('24', "[24] Entrada por devolución del cliente"),
    ('25', "[25] Salida por devolución al proveedor"),
    ('26', "[26] Entrada para servicio de producción"),
    ('27', "[27] Salida por servicio de producción"),
    ('28', "[28] Ajuste por diferencia de inventario"),
    ('29', "[29] Entrada de bienes en préstamo"),
    ('30', "[30] Salida de bienes en préstamo"),
    ('31', "[31] Entrada de bienes en custodia"),
    ('32', "[32] Salida de bienes en custodia"),
    ('33', "[33] Muestras Médicas"),
    ('34', "[34] Publicidad"),
    ('35', "[35] Gastos de representación"),
    ('36', "[36] Retiro para entrega a trabajadores"),
    ('37', "[37] Retiro por convenio colectivo"),
    ('38', "[38] Retiro por sustitución de bien siniestrado"),
    ('99', "[99] Otros")
]


class AccountAccount(models.Model):
    _inherit = 'account.account'

    ple_selection = fields.Selection(
        selection_add=[
            ('stock_revaluation_book', '12.1 y 13.1 Registro del Inventario permanente')
        ]
    )

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('form'):
            tags = [('field', 'ple_selection')]
            arch, view = self.env['res.partner']._tags_invisible_per_country(arch, view, tags, [self.env.ref('base.pe')])
        return arch, view


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_catalog = fields.Selection(
        selection=[
            ('1', "[1] NACIONES UNIDAS (UNSPSC)"),
            ('3', "[3] GS1 (EAN-UCC)"),
            ('9', "[9] Otros")],
        string="Catálogo de existencia",
        help='Este código se usa en los libros PLE de inventario permanente y se valida con la tabla 13 del anexo 3'
    )
    stock_type = fields.Selection(
        selection=[
            ('01', "[01] Mercadería"),
            ('02', "[02] Productos terminados"),
            ('03', "[03] Materias Primas"),
            ('04', "[04] Envases"),
            ('05', "[05] Materiales Auxiliares"),
            ('06', "[06] Suministros"),
            ('07', "[07] Repuestos"),
            ('08', "[08] Enbalajes"),
            ('09', "[09] SubProductos"),
            ('10', "[10] Desechos y desperdicios"),
            ('91', "[91] Otros 1"),
            ('92', "[92] Otros 2"),
            ('93', "[93] Otros 3"),
            ('94', "[94] Otros 4"),
            ('95', "[95] Otros 5"),
            ('96', "[96] Otros 6"),
            ('97', "[97] Otros 7"),
            ('98', "[98] Otros 8"),
            ('99', "[99] Otros"),
        ],
        string="Tipo de existencia",
        help='Este código se usa en los libros PLE de inventario permanente y se valida con la tabla 13 del anexo 3'
    )

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('form'):
            tags = [('field', 'stock_catalog'), ('field', 'stock_type')]
            arch, view = self.env['res.partner']._tags_invisible_per_country(arch, view, tags, [self.env.ref('base.pe')])
        return arch, view


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_products_stock(self, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        to_date = fields.Datetime.to_datetime(to_date)
        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            date_date_expected_domain_from = [
                '|',
                '&',
                ('state', '=', 'done'),
                ('date', '<=', from_date),
                '&',
                ('state', '!=', 'done'),
                ('date_deadline', '<=', from_date),
            ]
            domain_move_in += date_date_expected_domain_from
            domain_move_out += date_date_expected_domain_from
        if to_date:
            date_date_expected_domain_to = [
                '|',
                '&',
                ('state', '=', 'done'),
                ('date', '<=', to_date),
                '&',
                ('state', '!=', 'done'),
                ('date_deadline', '<=', to_date),
            ]
            domain_move_in += date_date_expected_domain_to
            domain_move_out += date_date_expected_domain_to

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
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
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                     Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'],
                                                     orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                      Move.read_group(domain_move_out_done, ['product_id', 'product_qty'],
                                                      ['product_id'], orderby='id'))

        filter_products_ids = self.env['product.product']
        for product in self.with_context(prefetch_fields=False):
            res = dict()
            product_id = product.id
            if not product_id:
                res[product_id] = dict.fromkeys(
                    ['qty_available', 'free_qty', 'incoming_qty', 'outgoing_qty', 'virtual_available'],
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
            reserved_quantity = quants_res.get(product_id, [False, 0.0])[1]
            res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
            res[product_id]['free_qty'] = float_round(qty_available - reserved_quantity, precision_rounding=rounding)
            res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0),
                                                          precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0),
                                                          precision_rounding=rounding)
            res[product_id]['virtual_available'] = float_round(
                qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                precision_rounding=rounding)
            if res[product_id]['qty_available'] != 0:
                filter_products_ids += product
        return filter_products_ids


class StockLocation(models.Model):
    _inherit = 'stock.location'

    correlative = fields.Integer(
        string='Correlativo'
    )
    storehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', 
        string="Almacen"
    )

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('form'):
            tags = [('field', 'correlative')]
            arch, view = self.env['res.partner']._tags_invisible_per_country(arch, view, tags, [self.env.ref('base.pe')])
        return arch, view


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    type_operation_sunat = fields.Selection(
        selection=stock_picking_reason,
        string='Tipo de Operación SUNAT'
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super(StockPicking, self).create(vals_list)
        for record in records:
            if not record.type_operation_sunat:
                record.onchange_type_operation_sunat()
        return records

    @api.onchange('location_id', 'location_dest_id', 'picking_type_id')
    def onchange_type_operation_sunat(self):
        if self.picking_type_id:
            code = self.picking_type_id.code
            flag1 = self.check_picking_type_id_code(self.location_id, code)
            flag2 = self.check_picking_type_id_code(self.location_dest_id, code)
            if flag1 and flag2:
                self.type_operation_sunat = self.picking_type_id.ple_revert_id
            else:
                self.type_operation_sunat = self.picking_type_id.ple_reason_id

    @staticmethod
    def check_picking_type_id_code(location, code):
        if location and location.usage == code:
            return True
        else:
            return False

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('form'):
            tags = [('field', 'type_operation_sunat')]
            arch, view = self.env['res.partner']._tags_invisible_per_country(arch, view, tags, [self.env.ref('base.pe')])
        return arch, view


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    ple_reason_id = fields.Selection(
        selection=stock_picking_reason,
        string="PLE - Razón"
    )
    ple_revert_id = fields.Selection(
        selection=stock_picking_reason,
        string="PLE - Revert"
    )

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('form'):
            tags = [('field', 'ple_reason_id'), ('field', 'ple_revert_id')]
            arch, view = self.env['res.partner']._tags_invisible_per_country(arch, view, tags, [self.env.ref('base.pe')])
        return arch, view
