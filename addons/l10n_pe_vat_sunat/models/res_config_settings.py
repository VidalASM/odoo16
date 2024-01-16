# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
  
    annexed_locals = fields.Boolean('Annexed Locals', related='company_id.annexed_locals', readonly=False)
    legal_representatives = fields.Boolean('Legal Representatives', related='company_id.legal_representatives', readonly=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        annexed_locals = params.get_param('l10n_pe_vat_sunat.annexed_locals')
        legal_representatives = params.get_param('l10n_pe_vat_sunat.legal_representatives')
        res.update(
            annexed_locals = annexed_locals,
            legal_representatives = legal_representatives,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("l10n_pe_vat_sunat.annexed_locals", self.annexed_locals)
        self.env['ir.config_parameter'].sudo().set_param("l10n_pe_vat_sunat.legal_representatives", self.legal_representatives)