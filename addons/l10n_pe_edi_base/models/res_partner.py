###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

from odoo import models

from odoo.addons.iap.tools import iap_tools

DEFAULT_IAP_ENDPOINT = "https://iap.odoofact.pe"


class ResPartner(models.Model):
    _inherit = "res.partner"

    def connect_to_iap(self, endpoint, params):
        ir_params = self.env["ir.config_parameter"].sudo()
        default_endpoint = ir_params.get_param(
            "odoofact_iap_endpoint", DEFAULT_IAP_ENDPOINT
        )
        iap_server_url = ir_params.get_param("l10n_pe_edi_endpoint", default_endpoint)
        return iap_tools.iap_jsonrpc(iap_server_url + endpoint, params=params)
