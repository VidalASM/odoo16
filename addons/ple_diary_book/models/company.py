from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    code_prefix = fields.Selection(
        selection=[
            ('01', '01 - Plan Contable General Empresarial'),
            ('02', '02 - Plan Contable General Revisado'),
            ('03', '03 - Plan de cuentas para empresas del sistema financiero supervisadas por la SBS'),
            ('04', '04 - Plan de cuentas para entidades prestadoras de Salud supervisadas por la SBS'),
            ('05', '05 - Plan de cuentas para empresas del sistema asegurador supervisadas por la SBS'),
            ('06', '06 - Plan de Cuentas de las AFP supervisadas por la SBS'),
            ('99', '99 - Otros')
        ],
        string='Plan de Cuentas',
        help="""Validar con tabla 17 correspondiente a los parámetros para libros electrónicos de SUNAT, consignar alguno de estos códigos de 02 dígitos:
            01 - Plan Contable General Empresarial
            02 - Plan Contable General Revisado
            03 - Plan de cuentas para empresas del sistema financiero supervisadas por la SBS
            04 - Plan de cuentas para entidades prestadoras de Salud supervisadas por la SBS
            05 - Plan de cuentas para empresas del sistema asegurador supervisadas por la SBS
            06 - Plan de Cuentas de las AFP supervisadas por la SBS
            99 - Otros
        """
    )
