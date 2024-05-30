from odoo import models, fields


class FinancialEntitySunatCode(models.Model):
    _inherit = 'res.bank'

    sunat_bank_code = fields.Selection(
        string='Código Sunat',
        selection=[
            ('01', "01 - CENTRAL DE RESERVA DEL PERU"),
            ('02', "02 - DE CREDITO DEL PERU"),
            ('03', "03 - INTERNACIONAL DEL PERU"),
            ('05', "05 - LATINO"),
            ('07', "07 - CITIBANK DEL PERU S.A."),
            ('08', "08 - STANDARD CHARTERED"),
            ('09', "09 - SCOTIABANK PERU"),
            ('11', "11 - CONTINENTAL"),
            ('12', "12 - DE LIMA"),
            ('16', "16 - MERCANTIL"),
            ('18', "18 - NACION"),
            ('22', "22 - SANTANDER CENTRAL HISPANO"),
            ('23', "23 - DE  COMERCIO"),
            ('25', "25 - REPUBLICA"),
            ('26', "26 - NBK BANK"),
            ('29', "29 - BANCOSUR"),
            ('35', "35 - FINANCIERO DEL PERU"),
            ('37', "37 - DEL PROGRESO"),
            ('38', "38 - INTERAMERICANO FINANZAS"),
            ('39', "39 - BANEX"),
            ('40', "40 - NUEVO MUNDO"),
            ('41', "41 - SUDAMERICANO"),
            ('42', "42 - DEL LIBERTADOR"),
            ('43', "43 - DEL TRABAJO"),
            ('44', "44 - SOLVENTA"),
            ('45', "45 - SERBANCO SA."),
            ('46', "46 - BANK OF BOSTON"),
            ('47', "47 - ORION"),
            ('48', "48 - DEL PAIS"),
            ('49', "49 - MI BANCO"),
            ('50', "50 - BNP PARIBAS"),
            ('51', "51 - AGROBANCO"),
            ('53', "53 - HSBC BANK PERU S.A."),
            ('54', "54 - BANCO FALABELLA S.A."),
            ('55', "55 - BANCO RIPLEY"),
            ('58', "58 - BANCO AZTEXA DEL PERU"),
            ('99', "99 - OTROS")
        ]
    )
