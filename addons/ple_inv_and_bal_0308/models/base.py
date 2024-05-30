from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    ple_selection = fields.Selection(
        selection_add=[
            ('investment_property_cost_3_8',
             '3.8 Registro de Inventarios y Balances - Inversiones Mobiliarias - Costo'),
            ('investment_property_provision_3_8',
             '3.8 Registro de Inventarios y Balances - Inversiones Mobiliarias - Provisión')
        ])


class AccountMove(models.Model):
    _inherit = 'asset.intangible'

    title_code = fields.Selection(
        selection=[
            ('01', 'VALORES EMITIDOS O GARANTIZADOS POR EL ESTADO'),
            ('02', 'VALORES EMITIDOS O GARANTIZADOS POR EL SISTEMA FINANCIERO'),
            ('03', 'VALORES EMITIDOS POR LA EMPRESA'),
            ('04', 'OTROS INSTRUMENTOS FINANCIEROS REPRESENTATIVOS DE DEUDA'),
            ('05', 'CERTIFICADOS DE SUSCRIPCIÓN PREFERENTE'),
            ('06', 'ACCIONES REPRESENTATIVAS DE CAPITAL SOCIAL'),
            ('07', 'ACCIONES DE INVERSIÓN'),
            ('08', 'CERTIFICADO DE PARTICIPACIÓN DE FONDOS'),
            ('09', 'ASOCIACIONES EN PARTICIPACIÓN Y CONSORCIOS'),
            ('10', 'OTROS INSTRUMENTOS FINANCIEROS REPRESENTATIVOS DE DERECHO PATRIMONIAL'),
            ('99', 'OTROS TÍTULOS'),
        ],
        string='Código de titulo',
        required=False,
    )

    title_unit_value = fields.Float(
        string="Valor unitario del titulo",
        digits=(16, 2))
    total_amount_value = fields.Char(
        string="Cantidad del titulo",)
    
    
