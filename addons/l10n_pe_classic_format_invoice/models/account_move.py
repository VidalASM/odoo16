from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    related_tax_documents_code = fields.Selection([
        ('01', "Factura - emitida para corregir error en el RUC"),
        ('02', "Factura - emitida por anticipos"),
        ('03', "Boleta de venta - Emitida por anticipos"),
        ('04', "Ticket de salida - ENAPU"),
        ('05', "Código SCOP"),
        ('06', "Factura electrónica remitente"),
        ('07', "Guía de remisión remitente"),
        ('08', "Declaración de salida del depósito franco"),
        ('09', "Declaración simplificada de importación"),
        ('10', "Liquidación de compra - emitida por anticipos"),
        ('99', "Otros"),
    ], string='Código de documentos relacionados tributarios')
