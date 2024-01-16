###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

import base64

import requests

from odoo import api, models


class AccountInvoiceSend(models.TransientModel):
    _inherit = "account.invoice.send"

    @api.onchange("template_id")
    def onchange_template_id(self):
        res = super(AccountInvoiceSend, self).onchange_template_id()
        for wizard in self:
            Attachment = self.env["ir.attachment"]
            if wizard.template_id and wizard.composition_mode != "mass_mail":
                invoice_id = self.env[wizard.composer_id.model].browse(
                    wizard.composer_id.res_id
                )
                if invoice_id.l10n_pe_edi_request_id.link_xml:
                    r = requests.get(
                        invoice_id.l10n_pe_edi_request_id.link_xml, timeout=10
                    )
                    data_content = r.content
                    attachment_ids = []
                    data_attach = {
                        "name": invoice_id.name + ".xml",
                        "datas": base64.encodebytes(data_content),
                        "res_model": "mail.compose.message",
                        "res_id": 0,
                        "type": "binary",
                        # override default_type from context, possibly meant for another model!
                    }
                    attachment_ids.append(Attachment.create(data_attach).id)
                    wizard.write(
                        {
                            "attachment_ids": [
                                (
                                    6,
                                    0,
                                    wizard.composer_id.attachment_ids.ids
                                    + attachment_ids,
                                )
                            ]
                        }
                    )
        return res
