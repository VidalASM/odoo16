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


class L10nPeEdiMoveCancel(models.TransientModel):
    _name = "l10n_pe_edi.move.cancel"
    _description = "Send invoice cancel"

    description = fields.Char(string="Reason")

    def send_invoice_cancel(self):
        active_ids = self.env.context.get("active_ids", [])
        moves = self.env["account.move"].browse(active_ids)
        moves.write(
            {
                "l10n_pe_edi_cancel_reason": self.description,
            }
        )
        moves.action_document_cancel()
