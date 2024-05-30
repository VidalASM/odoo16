#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from odoo import api, fields, models


class AccountDebitNote(models.TransientModel):
    _inherit = "account.debit.note"

    def _get_type_debit_note(self):
        return self.env.ref("l10n_pe_edi_catalog.l10n_pe_edi_cat10_01").id

    available_journal_ids = fields.Many2many(
        comodel_name="account.journal", compute="_compute_available_journal_ids"
    )
    l10n_pe_edi_debit_type_id = fields.Many2one(
        comodel_name="l10n_pe_edi.catalog.10",
        string="Debit note type",
        default=_get_type_debit_note,
        help="Catalog 10: Types of Debit note",
    )
    journal_id = fields.Many2one(
        compute="_compute_journal_id", required=True, readonly=False, store=True
    )

    @api.depends("move_ids")
    def _compute_available_journal_ids(self):
        for rec in self:
            move_ids = self.env["account.move"].browse(rec.move_ids.ids)
            if all(move.l10n_pe_edi_is_einvoice for move in move_ids):
                rec.available_journal_ids = self.env["account.journal"].search(
                    [
                        ("l10n_latam_document_type_id.code", "=", "08"),
                        ("company_id", "=", self.env.company.id),
                    ]
                )

    @api.depends("move_ids", "available_journal_ids")
    def _compute_journal_id(self):
        for rec in self:
            move_ids = self.env["account.move"].browse(rec.move_ids.ids)
            if all(move.l10n_pe_edi_is_einvoice for move in move_ids):
                rec.journal_id = (
                    rec.available_journal_ids
                    and rec.available_journal_ids[0]._origin
                    or False
                )

    def _prepare_default_values(self, move):
        res = super(AccountDebitNote, self)._prepare_default_values(move)
        res.update(
            {
                "l10n_pe_edi_debit_type_id": self.l10n_pe_edi_debit_type_id.id,
                "l10n_latam_document_type_id": self.journal_id.l10n_latam_document_type_id.id,
            }
        )
        return res
