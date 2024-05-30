###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_l10n_pe_edi_send_invoice = fields.Boolean(
        related="pos_config_id.l10n_pe_edi_send_invoice", readonly=False
    )
    pos_invoice_journal_ids = fields.Many2many(
        related="pos_config_id.invoice_journal_ids", readonly=False
    )
    pos_default_partner_id = fields.Many2one(
        related="pos_config_id.default_partner_id", readonly=False
    )
    pos_auto_check_invoice = fields.Boolean(
        related="pos_config_id.auto_check_invoice", readonly=False
    )

    pos_receipt_design = fields.Many2one(
        related="pos_config_id.receipt_design",
        string="Receipt Design",
        help="Choose any receipt design",
        compute="_compute_pos_is_custom_receipt",
        readonly=False,
        store=True,
    )
    pos_design_receipt = fields.Text(
        related="pos_config_id.design_receipt", string="Receipt XML"
    )
    pos_is_custom_receipt = fields.Boolean(
        related="pos_config_id.is_custom_receipt", readonly=False, store=True
    )

    @api.depends("pos_is_custom_receipt", "pos_config_id")
    def _compute_pos_is_custom_receipt(self):
        for res_config in self:
            if res_config.pos_is_custom_receipt:
                res_config.pos_receipt_design = res_config.pos_config_id.receipt_design
            else:
                res_config.pos_receipt_design = False
