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


class EdiPickingNumber(models.Model):
    _name = "l10n_pe_edi.picking.number"
    _description = "Reference Guides"

    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Move",
        required=True,
        readonly=True,
        index=True,
        ondelete="cascade",
    )
    name = fields.Char(
        string="Number", required=True, help="Sintaxt serial TXXX-XXXX or 0XXX-XXXX"
    )
    type = fields.Selection(
        selection=[("1", "SENDER REFERRAL GUIDE"), ("2", "CARRIER REFERRAL GUIDE")],
        default="1",
        required=True,
    )
