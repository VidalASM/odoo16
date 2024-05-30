# -*- coding: utf-8 -*-

from datetime import timedelta, date

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DocumentType(models.Model):
    _name = 'documents.type'

    name = fields.Char(required=True)
    user_ids = fields.Many2many('res.users')
    notify_bfr = fields.Integer()


class Document(models.Model):
    _inherit = 'documents.document'
    expiry_date = fields.Date('Expiry Date', tracking=True, default=fields.Date.today() + relativedelta(years=1))
    notify_before = fields.Integer('Notify Before', tracking=True, default=30)
    document_type = fields.Many2one('documents.type')


    def mail_reminder(self):
        date_now = date.today() + timedelta(days=1)
        match = self.search([])
        for i in match:
            if i.expiry_date:
                notify_before = i.document_type and i.document_type.notify_bfr or i.notify_before
                users = i.document_type and i.document_type.user_ids
                exp_date = i.expiry_date - timedelta(days=notify_before)
                if date_now == exp_date:
                    template_id = self.env.ref('kg_document_expiry.notify_document_expire_email').id
                    for user in users:
                        try:
                            template = self.env['mail.template'].browse(template_id)
                            template.with_context(email_to=user.email).send_mail(i.id, email_values={
                                'author_id': self.env.user.partner_id.id,
                                'email_to': user.email}, force_send=True)
                        except UserError as e:
                            raise UserError(_("Error while sending email to user %s: %s" % (user.name, e)))




