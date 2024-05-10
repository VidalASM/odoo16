from odoo import models, fields


class AccountGroup(models.Model):
    _inherit = 'account.group'

    type_group = fields.Selection(
        selection=[
            ('balance', 'Balance'),
            ('function', 'Income by Function'),
            ('nature', 'Income by Nature'),
            ('both', 'Both Incomes')
        ],
        help='The attribute filled in this field determines in which column of the trial balance the balance will appear',
        string='Group Type'
    )
