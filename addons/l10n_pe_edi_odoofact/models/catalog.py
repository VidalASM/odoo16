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


class L10nLatamDocumentType(models.Model):
    _inherit = "l10n_latam.document.type"

    type_of = fields.Selection(
        selection=[
            ("1", "FACTURA"),
            ("2", "BOLETA"),
            ("3", "NOTA DE CREDITO"),
            ("4", "NOTA DE DEBITO"),
        ],
        string="Document Type",
        help="Used by Odoofact\n1 = FACTURA\n2 = BOLETA\n3 = NOTA DE CREDITO\n4 = "
        "NOTA DE DEBITO",
    )
