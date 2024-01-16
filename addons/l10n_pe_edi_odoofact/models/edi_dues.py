#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from odoo import fields, models


class EdiDues(models.Model):
    _name = "l10n_pe_edi.dues"
    _description = "Dues"

    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Move",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    currency_id = fields.Many2one(related="move_id.currency_id")
    dues_number = fields.Integer()
    paid_date = fields.Date()
    amount = fields.Monetary(currency_field="currency_id")
