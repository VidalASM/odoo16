from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    origin_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Documento Rectificado',
        domain="[('id', '!=', id)]"
    )
    origin_number = fields.Char(string='Referencia Documento Rectificado')
    origin_l10n_latam_document_type_id = fields.Many2one(
        comodel_name='l10n_latam.document.type',
        string='Tipo Documento Rectificado'
    )
    sunat_origin_code = fields.Char(
        related='origin_l10n_latam_document_type_id.code',
        string='Código Origen Sunat'
    )
    origin_invoice_date = fields.Date(string='Fecha Rectificado')

    @api.onchange('origin_move_id', 'reversed_entry_id', 'debit_origin_id')
    def _onchange_origin_move_id(self):
        origin_move_id = self.origin_move_id or self.reversed_entry_id or self.debit_origin_id or False
        document_type, invoice_date, number = self.get_data_from_origin_move_id(origin_move_id)
        self.update({
            'origin_l10n_latam_document_type_id': document_type,
            'origin_number': number,
            'origin_invoice_date': invoice_date
        })

    @staticmethod
    def get_data_from_origin_move_id(origin_move_id):
        document_type = False
        invoice_date = False
        number = False
        if origin_move_id and origin_move_id.l10n_latam_document_type_id:
            if origin_move_id.payment_reference and origin_move_id.move_type != 'out_invoice':
                number = origin_move_id.payment_reference.replace(' ', '')
            elif origin_move_id.ref and origin_move_id.move_type != 'out_invoice':
                number = origin_move_id.ref.replace(' ', '')
            elif origin_move_id.move_type == 'out_invoice':
                number = origin_move_id.name.replace(' ', '')
            else:
                number = ''
            document_type = origin_move_id.l10n_latam_document_type_id.id
            invoice_date = origin_move_id.invoice_date
        return document_type, invoice_date, number

    def _reverse_moves(self, default_values_list=None, cancel=False):
        list_moves = super(AccountMove, self)._reverse_moves(default_values_list=default_values_list, cancel=cancel)
        for obj_move in list_moves:
            obj_move._onchange_origin_move_id()
        return list_moves


class AccountDebitNote(models.TransientModel):
    _inherit = 'account.debit.note'

    def _prepare_default_values(self, move):
        default_values = super(AccountDebitNote, self)._prepare_default_values(move)
        if default_values['debit_origin_id']:
            debit_origin_id = self.env['account.move'].browse(default_values['debit_origin_id'])
            document_type, invoice_date, number = self.get_data_from_origin_debit_note_move_id(debit_origin_id)
            default_values.update({
                'origin_l10n_latam_document_type_id': document_type,
                'origin_number': number,
                'origin_invoice_date': invoice_date
            })
        return default_values

    @staticmethod
    def get_data_from_origin_debit_note_move_id(origin_move_id):
        document_type = False
        invoice_date = False
        number = False
        if origin_move_id and origin_move_id.l10n_latam_document_type_id:
            if origin_move_id.payment_reference:
                number = origin_move_id.payment_reference.replace(' ', '')
            elif origin_move_id.ref:
                number = origin_move_id.ref.replace(' ', '')
            else:
                number = ''
            document_type = origin_move_id.l10n_latam_document_type_id.id
            invoice_date = origin_move_id.invoice_date
        return document_type, invoice_date, number
