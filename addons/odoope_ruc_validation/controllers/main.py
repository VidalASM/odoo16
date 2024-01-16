#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from odoo.http import Controller, request, route


class BannerController(Controller):
    @route("/credit_status", type="json", auth="user")
    def credit_status(self):
        credit = request.env["iap.account"].get_credits("l10n_pe_data")
        credit_url = request.env["iap.account"].get_credits_url("l10n_pe_data")
        return {
            "html": request.env["ir.ui.view"]._render_template(
                "odoope_ruc_validation.credit_banner",
                {"credit": credit, "credit_url": credit_url},
            )
        }
