from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    ple_selection = fields.Selection(
        selection_add=[
            ('assets_book_remuneration_contributions_payable',
             '3.11 Libro de remuneraciones y participaciones por pagar'),
            ('assets_book_employee_benefits', '3.14 Libro de beneficios sociales de los empleados')
        ])
