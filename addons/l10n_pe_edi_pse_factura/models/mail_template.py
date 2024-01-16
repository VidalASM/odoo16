from odoo import models

class MailTemplate(models.Model):
    _inherit = "mail.template"

    def _get_edi_attachments(self, document):
        if not document.sudo().attachment_id or document.edi_format_id.code != 'pe_pse':
            return super()._get_edi_attachments(document)
        if document.state=='to_send' and document.move_id.l10n_pe_edi_pse_uid and document.move_id.company_id.l10n_pe_edi_provider=='conflux':
            #TODO Download XML file
            pass
        return {'attachments': document.edi_format_id._l10n_pe_edi_unzip_all_edi_documents(document.sudo().attachment_id.datas)}