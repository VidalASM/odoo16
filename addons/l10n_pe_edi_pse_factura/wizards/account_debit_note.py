# -*- coding: utf-8 -*-
from odoo import fields, models

class AccountDebitNote(models.TransientModel):
    _inherit = 'account.debit.note'

    def _prepare_default_values(self, move):
        values = super()._prepare_default_values(move)
        if move.company_id.country_id.code == "PE" and move.journal_id.l10n_latam_use_documents:
            values.update({
                'l10n_pe_edi_rectification_ref_type': move.l10n_latam_document_type_id.id,
                'l10n_pe_edi_rectification_ref_number': move.name.replace(' ',''),
                'l10n_pe_edi_rectification_ref_date': move.invoice_date,
            })
        return values