from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    serie_correlative = fields.Char(
        string='Serie-Correlativo',
        compute='_compute_serie_correlative_payment',
        store=True,
    )

    @api.depends('ref', 'name')
    def _compute_serie_correlative_payment(self):
        for move in self:
            if move.move_type in ['in_invoice', 'in_refund', 'in_receipt']:
                move.serie_correlative = move.ref
                (move.invoice_line_ids | move.line_ids).write({'serie_correlative': move.ref})
            elif move.move_type in ['out_invoice', 'out_refund', 'out_receipt'] and not move.journal_id.l10n_latam_use_documents and move.journal_id.type != 'sale':
                continue
            elif move.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
                move.serie_correlative = move.name
                (move.invoice_line_ids | move.line_ids).write({'serie_correlative': move.name})
            elif move.move_type == 'entry':
                ids = [line.id for line in move.line_ids._all_reconciled_lines()]
                if ids:
                    self.env.cr.execute("""
                        SELECT l10n_latam_document_type_id, serie_correlative
                        FROM account_move_line
                        WHERE id in %s and serie_correlative is not NULL""", [tuple(ids)]
                    )
                    is_document_type = self.env.cr.dictfetchall()
                    if is_document_type:
                        document_type = is_document_type[0]['l10n_latam_document_type_id']
                        serie_correlative = is_document_type[0]['serie_correlative']
                        for id_line in ids:
                            self.env.cr.execute("""
                                SELECT l10n_latam_document_type_id, serie_correlative
                                FROM account_move_line
                                WHERE id=%s """, [(id_line)]
                            )
                            is_document_type = self.env.cr.dictfetchall()
                            if not is_document_type[0]['l10n_latam_document_type_id']:
                                self.env['account.move.line'].search([('id', '=', id_line)]).write({
                                    'l10n_latam_document_type_id': document_type,
                                    'serie_correlative': serie_correlative
                                })

    def _compute_name(self):
        super()._compute_name()
        for move in self:
            if move.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
                for line in move.invoice_line_ids:
                    line.serie_correlative = move.name
                for line in move.line_ids:
                    line.serie_correlative = move.name


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    serie_correlative = fields.Char(
        string='Serie-Correlativo',
        store=True
    )
    move_type = fields.Selection(
        related='move_id.move_type'
    )
    serie_correlative_is_readonly = fields.Boolean(
        string='Es editable',
        compute='_compute_serie_correlative_is_readonly',
        store=True
    )

    def create(self, vals_list):
        lines = super(AccountMoveLine, self).create(vals_list)
        index = 0
        for line in lines:
            if vals_list and isinstance(vals_list, list) and 'l10n_latam_document_type_id' in vals_list[index].keys():
                doc = self.env['l10n_latam.document.type'].search([('id', '=', vals_list[index]['l10n_latam_document_type_id'])])
                if doc.id >= 0:
                    line.l10n_latam_document_type_id = doc
            index += 1
        return lines

    @api.depends('move_id')
    def _compute_serie_correlative_is_readonly(self):
        for rec in self:
            if rec.move_id:
                if rec.move_id.move_type in ['out_invoice', 'out_refund',
                                             'out_receipt'] and not rec.move_id.journal_id.l10n_latam_use_documents and rec.move_id.journal_id.type == 'sale':
                    rec.serie_correlative_is_readonly = False
                elif rec.move_id.move_type == 'entry':
                    rec.serie_correlative_is_readonly = False
                else:
                    rec.serie_correlative_is_readonly = True

    # Extract type of document from the invoices to the other accounting entries
    def reconcile(self):
        res = super(AccountMoveLine, self).reconcile()
        if 'full_reconcile' in res.keys():
            account_reconcile = res['full_reconcile']

            document_type = None
            serie_correlative = None
            ids = []

            def update_info(move_line):
                nonlocal document_type, serie_correlative
                if move_line.move_id.l10n_latam_document_type_id and move_line.move_id.serie_correlative:
                    document_type = move_line.move_id.l10n_latam_document_type_id
                    serie_correlative = move_line.move_id.serie_correlative

            for move_line in account_reconcile.reconciled_line_ids:
                update_info(move_line)
                if move_line.move_id.move_type == 'entry':
                    ids.extend([line.id for line in move_line.move_id.line_ids._all_reconciled_lines()])
            if self.full_reconcile_id:
                for line in self.full_reconcile_id.reconciled_line_ids:
                    update_info(line)
            if document_type and ids:
                ids.append(ids[-1] - 1)
                for id_line in ids:
                    self.env.cr.execute("""SELECT l10n_latam_document_type_id 
                                            FROM account_move_line
                                            WHERE id=%s """, [(id_line)])
                    is_document_type = self.env.cr.dictfetchall()
                    if is_document_type and is_document_type[0] and not is_document_type[0]['l10n_latam_document_type_id']:
                        self.search([('id', '=', id_line)]).write({
                            'l10n_latam_document_type_id': document_type.id,
                            'serie_correlative': serie_correlative
                        })
            if self.statement_id and document_type:
                for line in self.statement_id.line_ids:
                    for move_line in line.move_id.line_ids:
                        if document_type and serie_correlative:
                            move_line.l10n_latam_document_type_id = document_type
                            move_line.serie_correlative = serie_correlative
        return res


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.depends('move_id.line_ids.matched_debit_ids', 'move_id.line_ids.matched_credit_ids')
    def _compute_stat_buttons_from_reconciliation(self):
        super(AccountPayment, self)._compute_stat_buttons_from_reconciliation()
        for pay in self:
            serie_correlative = False
            document_type = False
            for move in pay.reconciled_invoice_ids:
                for line in move.line_ids:
                    if line.serie_correlative:
                        serie_correlative = line.serie_correlative
                    if line.l10n_latam_document_type_id:
                        document_type = line.l10n_latam_document_type_id
            for line in pay.move_id.line_ids:
                if line:
                    if document_type:
                        self._cr.execute("""UPDATE account_move_line
                                        SET l10n_latam_document_type_id=%s
                                        WHERE id=%s """,
                                         (document_type.id, line.id))
                    if serie_correlative:
                        self._cr.execute("""UPDATE account_move_line
                                        SET serie_correlative=%s
                                        WHERE id=%s """,
                                        (serie_correlative, line.id))