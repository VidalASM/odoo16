from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    detraction_id = fields.Many2one(
        comodel_name='account.spot.detraction',
        string='Detracción'
    )
    retention_id = fields.Many2one(
        comodel_name='account.spot.retention',
        string='Retención',
    )
    voucher_payment_date = fields.Date(
        string='Fecha pago'
    )
    voucher_number = fields.Char(
        string='Número recibo'
    )
    operation_type_detraction = fields.Selection(
        selection=[
            ('01', 'Venta de Bienes o Pres. Serv.'),
            ('02', 'Retiro de Bienes Gravados IGV'),
            ('03', 'Translado que No son Venta'),
            ('04', 'Venta a través de Bolsa de Productos'),
            ('05', 'Venta de Bienes exonerados del IGV')
        ], 
        string='Tipo operación'
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    voucher_payment_date = fields.Date(
        related='move_id.voucher_payment_date',
        string='Fecha pago',
        store=True
    )
    voucher_number = fields.Char(
        related='move_id.voucher_number',
        string='Número recibo',
        store=True
    )
