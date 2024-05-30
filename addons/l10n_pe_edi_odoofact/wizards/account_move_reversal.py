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


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def _get_type_credit_note(self):
        return self.env.ref("l10n_pe_edi_catalog.l10n_pe_edi_cat09_01").id

    l10n_pe_edi_reversal_type_id = fields.Many2one(
        comodel_name="l10n_pe_edi.catalog.09",
        string="Credit note type",
        default=_get_type_credit_note,
        help="Catalog 09: Types of Credit note",
    )

    @api.depends("move_ids")
    def _compute_available_journal_ids(self):
        res = super(AccountMoveReversal, self)._compute_available_journal_ids()
        for rec in self:
            move_ids = self.env["account.move"].browse(rec.move_ids.ids)
            if all(move.l10n_pe_edi_is_einvoice for move in move_ids):
                rec.available_journal_ids = self.env["account.journal"].search(
                    [
                        ("l10n_latam_document_type_id.code", "=", "07"),
                        ("company_id", "=", self.env.company.id),
                    ]
                )
        return res

    @api.depends("move_ids", "available_journal_ids")
    def _compute_journal_id(self):
        res = super(AccountMoveReversal, self)._compute_journal_id()
        for rec in self:
            move_ids = self.env["account.move"].browse(rec.move_ids.ids)
            if all(move.l10n_pe_edi_is_einvoice for move in move_ids):
                rec.journal_id = (
                    rec.available_journal_ids
                    and rec.available_journal_ids[0]._origin
                    or False
                )
        return res

    @api.depends("journal_id")
    def _compute_document_type(self):
        for rec in self:
            rec.l10n_latam_document_type_id = rec.journal_id.l10n_latam_document_type_id

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res.update(
            {
                "l10n_pe_edi_reversal_type_id": self.l10n_pe_edi_reversal_type_id.id,
            }
        )
        return res

    def reverse_moves(self):
        self.ensure_one()
        res = super(AccountMoveReversal, self).reverse_moves()
        new_moves = self.env["account.move"].browse(self.new_move_ids.ids)
        for move in new_moves:
            if (
                move.l10n_pe_edi_is_einvoice
                and move.l10n_pe_edi_shop_id
                and not move.l10n_pe_edi_request_id
            ):
                document_type = self.env["l10n_pe_edi.request.document.type"].search(
                    [("code", "=", move.l10n_latam_document_type_id.code)], limit=1
                )
                request_id = self.env["l10n_pe_edi.request"].create(
                    {
                        "company_id": move.company_id.id,
                        "l10n_pe_edi_shop_id": move.l10n_pe_edi_shop_id
                        and move.l10n_pe_edi_shop_id.id
                        or False,
                        "l10n_pe_edi_document_type": move.l10n_latam_document_type_id
                        and move.l10n_latam_document_type_id.code
                        or False,
                        "l10n_pe_edi_document_type_id": document_type
                        and document_type.id
                        or False,
                        "document_number": move.name,
                        "document_date": move.invoice_date,
                        "model": move._name,
                        "res_id": move.id,
                    }
                )
                move.l10n_pe_edi_request_id = request_id.id
        return res
