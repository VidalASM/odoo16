from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def check_vat_pe(self, vat):
        return bool(vat)
