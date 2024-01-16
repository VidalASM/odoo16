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


class AccountJournal(models.Model):
    _inherit = "account.journal"

    l10n_document_internal_type = fields.Char(
        string="Internal Type",
        compute="_compute_l10n_document_internal_type",
        store=True,
    )

    @api.depends("l10n_latam_document_type_id.internal_type")
    def _compute_l10n_document_internal_type(self):
        for journal in self:
            if journal.l10n_latam_document_type_id:
                journal.l10n_document_internal_type = (
                    journal.l10n_latam_document_type_id.internal_type
                )
            else:
                journal.l10n_document_internal_type = False
