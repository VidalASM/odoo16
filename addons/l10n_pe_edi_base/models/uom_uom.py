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


class UomUom(models.Model):
    _inherit = "uom.uom"

    l10n_pe_edi_uom_code_id = fields.Many2one(
        comodel_name="l10n_pe_edi.catalog.03",
        string="SUNAT code",
        help="Unit code that relates to a product in order to identify what measure "
        "unit it uses",
    )
