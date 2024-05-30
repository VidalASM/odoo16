from odoo import fields, models, api



class AccountMove(models.Model):
    _inherit = 'account.move'

    carrier_ref_number = fields.Char('Guía(s) de Remisión')
    exist_advance = fields.Boolean(compute='_compute_exist_advance')

    @api.depends('invoice_line_ids')
    def _compute_exist_advance(self):
        for move in self:
            move.exist_advance = True
            for line in move.invoice_line_ids:
                if line.product_id.exist_advance:
                    move.exist_advance = False