from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_doubtful_accounts = fields.Many2one(
        string='Factura para cobranza dudosa',
        comodel_name='account.move',
        help="Este campo sirve para colocar la factura para provisión de cuentas incobrables."
             "\n\n"
             "Si viene de un asiento contable. POR FAVOR, deberá colocar en la ETIQUETA de la cuenta 19 el siguiente formato\n "
             "(Tipo de Doc.Serie del CPE.Correlativo del CPE.Fecha de emisión del CPE), todo pegado y separado por puntos. Es de carácter obligatorio.",
    )
