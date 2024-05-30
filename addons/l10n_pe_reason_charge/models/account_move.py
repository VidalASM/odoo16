from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    exist_advance = fields.Boolean(compute='_compute_exist_advance')

    @api.onchange('invoice_line_ids')
    def _compute_exist_advance(self):
        for move in self:
            move.exist_advance = False
            for line in move.invoice_line_ids:
                if line.product_id.product_tmpl_id.l10n_pe_advance:
                    move.exist_advance = True
