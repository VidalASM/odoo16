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


class L10nPeEdiSupplier(models.Model):
    _name = "l10n_pe_edi.supplier"
    _description = "PSE/OSE Supplier"

    code = fields.Char(required=True)
    name = fields.Char(size=128, index=True, required=True)
    control_url = fields.Char(string="URL for searching electronic documents")
    resume_url = fields.Char(string="URL for resume documents")
    authorization_message = fields.Html(
        help="The message will be printed on the invoice",
        translate=True,
        sanitize=False,
    )
