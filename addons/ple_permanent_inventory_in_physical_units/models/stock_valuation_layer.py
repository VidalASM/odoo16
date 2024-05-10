from odoo import api, models, fields

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
    ('99', "[99] Otros"),
]


class StockValuationLayer(models.Model):

    _inherit = 'stock.valuation.layer'

    sunat_operation_type = fields.Selection(
        stock_picking_reason,
        string='Tipo de operación SUNAT',
    )
    
    account_move_id = fields.Many2one(check_company=False)