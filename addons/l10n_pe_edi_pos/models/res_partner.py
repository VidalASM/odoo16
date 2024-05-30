###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create_from_ui(self, partner):
        if partner.get("l10n_latam_identification_type_id", False):
            partner.update(
                {
                    "l10n_latam_identification_type_id": int(
                        partner.get("l10n_latam_identification_type_id")
                    )
                }
            )
        res = super(ResPartner, self).create_from_ui(partner)
        return res
