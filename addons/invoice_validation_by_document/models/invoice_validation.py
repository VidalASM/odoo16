from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class InvoiceValidationDocument(models.Model):
    _inherit = 'l10n_latam.identification.type'

    invoice_validation_document = fields.Many2many(
        string='Comprobantes de pago aceptados',
        relation="relation_invoice_validation_document",
        comodel_name='l10n_latam.document.type'
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):

            if self.move_id.move_type == 'entry':
                self.l10n_latam_document_type_id = False
            else:
                if self.partner_id.l10n_latam_identification_type_id.name == 'RUC':
                    document = self.env['l10n_latam.document.type'].search([('name', '=', 'Factura')], limit=1)
                else:
                    document = self.env['l10n_latam.document.type'].search([('name', '=', 'Boleta')], limit=1)
                self.l10n_latam_document_type_id = document

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('name')
    def _compute_l10n_latam_document_number(self):
        for move in self:
            recs_with_name = move.filtered(lambda x: x.name != '/')
            for rec in recs_with_name:
                doc_code_prefix = rec.l10n_latam_document_type_id.doc_code_prefix
                name = rec.name
                if doc_code_prefix and name and rec.move_type == 'entry':
                    rec.name = name.split(" ", 1)[-1]
                rec.l10n_latam_document_number = rec.name
                if move.move_type in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
                    l10n_latam_document_number_list = move.l10n_latam_document_number.split(' ')
                    if len(l10n_latam_document_number_list) > 1:
                        move.l10n_latam_document_number = l10n_latam_document_number_list[1]
                    else:
                        move.l10n_latam_document_number = l10n_latam_document_number_list[0]
            remaining = move - recs_with_name
            remaining.l10n_latam_document_number = False
            move.fix_prefix_name()

    def action_post(self):
      
            for move in self:
                if  move.partner_id.l10n_latam_identification_type_id.invoice_validation_document:
                    
                    if move.l10n_latam_document_type_id in move.partner_id.l10n_latam_identification_type_id.invoice_validation_document or move.move_type == "entry" or not move.move_type:
                        super(AccountMove, move).action_post()
                    else:
                        raise UserError(
                            _('El tipo de documento que está intentando publicar, NO es el permitido, por favor verificar si es el que es el que está permitido'))
                else:
                    super(AccountMove, move).action_post()
                    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        super(AccountMove, self)._onchange_partner_id()
        if self.move_type == 'entry':
                self.l10n_latam_document_type_id = False
        else:
                if self.partner_id.l10n_latam_identification_type_id.name == 'RUC':
                    document = self.env['l10n_latam.document.type'].search([('name', '=', 'Factura')], limit=1)
                else:
                    document = self.env['l10n_latam.document.type'].search([('name', '=', 'Boleta')], limit=1)
                self.l10n_latam_document_type_id = document
        self.fix_prefix_name()

    def fix_prefix_name(self):
        all_documents = self.env['l10n_latam.document.type'].search([])
        all_prefix = []
        for doc in all_documents:
            if doc.doc_code_prefix not in all_prefix:
                all_prefix.append(doc.doc_code_prefix)
        if self.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            size_name = len(self.name)
            prefix_global = False
            new_name = False
            if all_prefix and self.l10n_latam_document_number:
                for prefix in all_prefix:
                    if self.l10n_latam_document_number and prefix and self.l10n_latam_document_number[:2] == prefix + ' ':
                        new_name = self.name.replace(prefix + ' ', '')
                    if self.l10n_latam_document_number and prefix and self.l10n_latam_document_number[0] == prefix:
                        prefix_global = prefix
            if new_name and size_name != len(new_name) and new_name and self.l10n_latam_document_type_id and self.l10n_latam_document_type_id.doc_code_prefix:
                self.name = self.l10n_latam_document_type_id.doc_code_prefix + ' ' + new_name
            if prefix_global and self.l10n_latam_document_number[0] == prefix_global and self.l10n_latam_document_number[:2] != prefix_global+' ':
                fix_name = self.name
                self.l10n_latam_document_number = fix_name

    @api.onchange('l10n_latam_document_type_id', 'l10n_latam_document_number')
    def _inverse_l10n_latam_document_number(self):
        all_documents = self.env['l10n_latam.document.type'].search([])
        all_prefix = []
        for doc in all_documents:
            if doc.doc_code_prefix not in all_prefix:
                all_prefix.append(doc.doc_code_prefix)
        for rec in self.filtered(lambda x: x.l10n_latam_document_type_id):
            if not rec.l10n_latam_document_number:
                rec.name = '/'
            else:
                l10n_latam_document_number = rec.l10n_latam_document_type_id._format_document_number(rec.l10n_latam_document_number)
                if rec.l10n_latam_document_number != l10n_latam_document_number:
                    rec.l10n_latam_document_number = l10n_latam_document_number
                rec.name = "%s %s" % (rec.l10n_latam_document_type_id.doc_code_prefix, l10n_latam_document_number)
                self.fix_prefix_name()
                if all_prefix:
                    for prefix in all_prefix:
                        if prefix:
                            if self.l10n_latam_document_number and self.l10n_latam_document_number[:2] and self.l10n_latam_document_number[:2] == prefix + ' ':
                                self.l10n_latam_document_number = self.l10n_latam_document_number.replace(prefix + ' ', '')
