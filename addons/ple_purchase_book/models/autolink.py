from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = 'account.account.tag'

    @api.model
    def automated_links(self):
        tags = {}
        tax = {}
        lines = self.env['account.tax.repartition.line']
        comp_id = min(self.env['res.company'].search([]).ids)

        if not comp_id:
            return
        # invoice
        tags['+P_BASE_GDG'] = self.env['account.account.tag'].search([('name', '=', '+P_BASE_GDG')], limit=1)
        tags['+P_TAX_GDG'] = self.env['account.account.tag'].search([('name', '=', '+P_TAX_GDG')], limit=1)
        tags['+P_BASE_NG'] = self.env['account.account.tag'].search([('name', '=', '+P_BASE_NG')], limit=1)

        # refund
        tags['-P_BASE_GDG'] = self.env['account.account.tag'].search([('name', '=', '-P_BASE_GDG')], limit=1)
        tags['-P_TAX_GDG'] = self.env['account.account.tag'].search([('name', '=', '-P_TAX_GDG')], limit=1)
        tags['-P_BASE_NG'] = self.env['account.account.tag'].search([('name', '=', '-P_BASE_NG')], limit=1)

        # tax
        tax['18%'] = self.env['account.tax'].search(
            [('name', 'in', ('18%', '18% C', '18% - C')), ('type_tax_use', '=', 'purchase'),
             ('company_id.id', '=', comp_id)], limit=1)
        tax['18% (Included in price)'] = self.env['account.tax'].search(
            [('name', 'in', ('18% (Included in price)', '18% (Inc. price)')), ('type_tax_use', '=', 'purchase'),
             ('company_id.id', '=', comp_id)], limit=1)
        tax['0% Exonerated'] = self.env['account.tax'].search(
            [('name', 'like', '0% Exonerated%'), ('type_tax_use', '=', 'purchase'), ('company_id.id', '=', comp_id)],
            limit=1)
        tax['0% Unaffected'] = self.env['account.tax'].search(
            [('name', 'like', '0% Unaffected%'), ('type_tax_use', '=', 'purchase'), ('company_id.id', '=', comp_id)],
            limit=1)
        tax['0% Free'] = self.env['account.tax'].search(
            [('name', 'like', '0% Free%'), ('type_tax_use', '=', 'purchase'), ('company_id.id', '=', comp_id)], limit=1)
        tax['18% IGV - DUA'] = self.env.ref('ple_purchase_book.account_tax_igv_18_dua')
        tax['IGV 18% CREDITO - NO DOMICILIADO'] = self.env.ref('ple_purchase_book.account_tax_igv_18_cred_no_dom')
        tax['IGV 18% NO DOMICILIADO'] = self.env.ref('ple_purchase_book.account_tax_igv_18_no_dom')

        # invoice

        lines.search([('id', 'in', tax['18%'].invoice_repartition_line_ids.ids), ('repartition_type', '=', 'base')],
                     limit=1
                     ).sudo().write({'tag_ids': tags['+P_BASE_GDG'].ids})
        lines.search([('id', 'in', tax['18%'].invoice_repartition_line_ids.ids), ('repartition_type', '=', 'tax')],
                     limit=1
                     ).sudo().write({'tag_ids': tags['+P_TAX_GDG'].ids})

        lines.search(
            [('id', 'in', tax['18% (Included in price)'].invoice_repartition_line_ids.ids),
             ('repartition_type', '=', 'base')], limit=1
        ).sudo().write({'tag_ids': tags['+P_BASE_GDG'].ids})
        lines.search(
            [('id', 'in', tax['18% (Included in price)'].invoice_repartition_line_ids.ids),
             ('repartition_type', '=', 'tax')], limit=1
        ).sudo().write({'tag_ids': tags['+P_TAX_GDG'].ids})

        lines.search(
            [('id', 'in', tax['0% Exonerated'].invoice_repartition_line_ids.ids), ('repartition_type', '=', 'base')],
            limit=1
        ).sudo().write({'tag_ids': tags['+P_BASE_NG'].ids})

        lines.search(
            [('id', 'in', tax['0% Unaffected'].invoice_repartition_line_ids.ids), ('repartition_type', '=', 'base')],
            limit=1
        ).sudo().write({'tag_ids': tags['+P_BASE_NG'].ids})

        lines.search(
            [('id', 'in', tax['0% Free'].invoice_repartition_line_ids.ids), ('repartition_type', '=', 'base')], limit=1
        ).sudo().write({'tag_ids': tags['+P_BASE_NG'].ids})

        # ------------------------------
        lines.search(
            [('id', 'in', tax['18% IGV - DUA'].invoice_repartition_line_ids.ids), ('repartition_type', '=', 'base')],
            limit=1
        ).sudo().write({'tag_ids': tags['+P_BASE_GDG'].ids})
        lines.search(
            [('id', 'in', tax['18% IGV - DUA'].invoice_repartition_line_ids.ids), ('repartition_type', '=', 'tax')],
            limit=1
        ).sudo().write({'tag_ids': tags['+P_TAX_GDG'].ids})

        lines.search(
            [('id', 'in', tax['IGV 18% CREDITO - NO DOMICILIADO'].invoice_repartition_line_ids.ids),
             ('repartition_type', '=', 'base')], limit=1
        ).sudo().write({'tag_ids': tags['+P_BASE_GDG'].ids})
        lines.search(
            [('id', 'in', tax['IGV 18% CREDITO - NO DOMICILIADO'].invoice_repartition_line_ids.ids),
             ('repartition_type', '=', 'tax')], limit=1
        ).sudo().write({'tag_ids': tags['+P_TAX_GDG'].ids})

        lines.search(
            [('id', 'in', tax['IGV 18% NO DOMICILIADO'].invoice_repartition_line_ids.ids),
             ('repartition_type', '=', 'base')], limit=1
        ).sudo().write({'tag_ids': tags['+P_BASE_NG'].ids})

        # refund

        lines.search([('id', 'in', tax['18%'].refund_repartition_line_ids.ids), ('repartition_type', '=', 'base')],
                     limit=1
                     ).sudo().write({'tag_ids': tags['-P_BASE_GDG'].ids})
        lines.search([('id', 'in', tax['18%'].refund_repartition_line_ids.ids), ('repartition_type', '=', 'tax')],
                     limit=1
                     ).sudo().write({'tag_ids': tags['-P_TAX_GDG'].ids})

        lines.search(
            [('id', 'in', tax['18% (Included in price)'].refund_repartition_line_ids.ids),
             ('repartition_type', '=', 'base')], limit=1
        ).sudo().write({'tag_ids': tags['-P_BASE_GDG'].ids})
        lines.search(
            [('id', 'in', tax['18% (Included in price)'].refund_repartition_line_ids.ids),
             ('repartition_type', '=', 'tax')], limit=1
        ).sudo().write({'tag_ids': tags['-P_TAX_GDG'].ids})

        lines.search(
            [('id', 'in', tax['0% Exonerated'].refund_repartition_line_ids.ids), ('repartition_type', '=', 'base')],
            limit=1
        ).sudo().write({'tag_ids': tags['-P_BASE_NG'].ids})

        lines.search(
            [('id', 'in', tax['0% Unaffected'].refund_repartition_line_ids.ids), ('repartition_type', '=', 'base')],
            limit=1
        ).sudo().write({'tag_ids': tags['-P_BASE_NG'].ids})

        lines.search(
            [('id', 'in', tax['0% Free'].refund_repartition_line_ids.ids), ('repartition_type', '=', 'base')], limit=1
        ).sudo().write({'tag_ids': tags['-P_BASE_NG'].ids})

        # ------------------------------
        lines.search(
            [('id', 'in', tax['18% IGV - DUA'].refund_repartition_line_ids.ids), ('repartition_type', '=', 'base')],
            limit=1
        ).sudo().write({'tag_ids': tags['-P_BASE_GDG'].ids})
        lines.search(
            [('id', 'in', tax['18% IGV - DUA'].refund_repartition_line_ids.ids), ('repartition_type', '=', 'tax')],
            limit=1
        ).sudo().write({'tag_ids': tags['-P_TAX_GDG'].ids})

        lines.search(
            [('id', 'in', tax['IGV 18% CREDITO - NO DOMICILIADO'].refund_repartition_line_ids.ids),
             ('repartition_type', '=', 'base')], limit=1
        ).sudo().write({'tag_ids': tags['-P_BASE_GDG'].ids})
        lines.search(
            [('id', 'in', tax['IGV 18% CREDITO - NO DOMICILIADO'].refund_repartition_line_ids.ids),
             ('repartition_type', '=', 'tax')], limit=1
        ).sudo().write({'tag_ids': tags['-P_TAX_GDG'].ids})

        lines.search(
            [('id', 'in', tax['IGV 18% NO DOMICILIADO'].refund_repartition_line_ids.ids),
             ('repartition_type', '=', 'base')], limit=1
        ).sudo().write({'tag_ids': tags['-P_BASE_NG'].ids})


class AccountJournals(models.Model):
    _inherit = 'account.journal'

    # overriding the @api.constrains (check_use_document) of the l10n_latam_invoice_document module
    @api.constrains('l10n_latam_use_documents')
    def check_use_document(self):
        pass

    @api.model
    def automated_creation(self):
        temp = self.env['account.journal'].search([('code', '=', 1662)], limit=1)

        args = {
                        'name': 'Formulario 1662',
                        'type': 'purchase',
                        'l10n_latam_use_documents': 0,
                        'ple_no_include': 0,
                        'ple_journal_correlative': 'M',
                        'default_account_id': self.env.ref('l10n_pe.1_chart6419').id,
                        'refund_sequence': 1,
                        'code': 1662,
            }

        if temp:
            temp.write(args)

        else:
            self.env['account.journal'].create(args)
