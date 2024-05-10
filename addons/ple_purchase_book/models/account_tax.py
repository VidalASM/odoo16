from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountTax(models.Model):
    _inherit = "account.tax"  

    @api.model
    def automated_links(self):

        country_id = self.env.ref('base.pe').id
        companies = self.sudo().env['res.company'].search([])
        print(companies)
        for company in companies:
            tax_ids = self.search([('company_id', '=', company.id)])
            for tax in tax_ids:
                if tax.company_id.country_id:
                    tax.country_id = tax.company_id.country_id.id

        company_id = None
        for company in companies:
            if company.country_id.id == country_id:
                company_id = company
                break
        
        # set taxes in peruvian company
        account_tax = self.env.ref('ple_purchase_book.account_tax_valor_ref')
        if account_tax.company_id.country_id.code != 'PE':        
            account_tax.company_id = company_id

        account_tax = self.env.ref('ple_purchase_book.account_tax_cif')
        if account_tax.company_id.country_id.code != 'PE':
            account_tax.company_id = company_id

        account_tax = self.env.ref('ple_purchase_book.account_tax_igv_adv')
        if account_tax.company_id.country_id.code != 'PE':
            account_tax.company_id = company_id

        # lines in taxes

        account_tax = self.env.ref('ple_purchase_book.account_tax_igv_18_dua')
        new_account = self.env['account.account'].search([('id', '=', self.env.ref('l10n_pe.chart40115').id)], limit=1)

        if account_tax.company_id.country_id.code != 'PE':
            account_tax.company_id = company_id

        if account_tax.invoice_repartition_line_ids and account_tax.refund_repartition_line_ids:
            for i in account_tax.invoice_repartition_line_ids:
                if i.repartition_type == 'tax':
                    i.account_id = new_account

            for i in account_tax.refund_repartition_line_ids:
                if i.repartition_type == 'tax':
                    i.account_id = new_account
        else:
            account_tax.write({
                'invoice_repartition_line_ids': [
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base',
                    }),

                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': new_account if new_account else False,
                    }),
                ],
                'refund_repartition_line_ids': [
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base',
                    }),

                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': new_account if new_account else False,
                    }),
                ],
            })
        account_tax = self.env.ref('ple_purchase_book.account_tax_igv_18_cred_no_dom')
        if account_tax.company_id.country_id.code != 'PE':
            account_tax.company_id = company_id
        account_id = self.env['account.account'].search([('code', 'like', '4011100')], limit=1)
        new_account = self.env['account.account'].search([('id', '=', self.env.ref('l10n_pe.chart40115').id)], limit=1)

        line_tax = account_tax.invoice_repartition_line_ids.search(
            [('id', 'in', account_tax.invoice_repartition_line_ids.ids), ('repartition_type', '=', 'tax')],
            limit=1
        )
        if account_tax.company_id.country_id.code != 'PE':
            account_tax.company_id = company_id
        if not line_tax:
            account_tax.write({
                'invoice_repartition_line_ids': [
                    (5, 0, 0),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base',
                    }),

                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': new_account,
                    }),
                ],
            })
        else:
            if line_tax.company_id == account_id.company_id:
                line_tax.account_id = account_id

        line_tax = account_tax.invoice_repartition_line_ids.search(
            [('id', 'in', account_tax.refund_repartition_line_ids.ids), ('repartition_type', '=', 'tax')],
            limit=1
        )
        if not line_tax:
            account_tax.write({
                'refund_repartition_line_ids': [
                    (5, 0, 0),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base',
                    }),

                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': new_account,
                    }),
                ],
            })
        else:
            if line_tax.company_id == account_id.company_id:
                line_tax.account_id = account_id

        account_tax = self.env.ref('ple_purchase_book.account_tax_igv_18_no_dom')
        new_account_1 = self.env['account.account'].search([('id', '=', self.env.ref('l10n_pe.chart1674').id)], limit=1)
        new_account_2 = self.env['account.account'].search([('id', '=', self.env.ref('l10n_pe.chart40112').id)],
                                                           limit=1)

        if account_tax.company_id.country_id.code != 'PE':
            account_tax.company_id = company_id
        if account_tax.invoice_repartition_line_ids and account_tax.refund_repartition_line_ids:
            for i in account_tax.invoice_repartition_line_ids:
                if i.repartition_type == 'tax' and i.factor_percent == 100 and i.company_id == new_account_1.company_id:
                    i.account_id = new_account_1
                if i.repartition_type == 'tax' and i.factor_percent == -100:
                    i.account_id = new_account_2

            for i in account_tax.refund_repartition_line_ids:
                if i.repartition_type == 'tax' and i.factor_percent == 100 and i.company_id == new_account_1.company_id:
                    i.account_id = new_account_1
                if i.repartition_type == 'tax' and i.factor_percent == -100:
                    i.account_id = new_account_2
        else:
            account_tax.sudo().write({
                'invoice_repartition_line_ids': [
                    (5, 0, 0),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base',
                    }),

                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': new_account_1,
                    }),

                    (0, 0, {
                        'factor_percent': -100,
                        'repartition_type': 'tax',
                        'account_id': new_account_2,
                    }),

                ],
                'refund_repartition_line_ids': [
                    (5, 0, 0),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base',
                    }),

                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': new_account_1,
                    }),

                    (0, 0, {
                        'factor_percent': -100,
                        'repartition_type': 'tax',
                        'account_id': new_account_2,
                    }),
                ]
            })

        account_tax = self.env.ref('ple_purchase_book.account_tax_perc_dua')
        new_account = self.env['account.account'].search([('id', '=', self.env.ref('l10n_pe.chart40113').id)])
        if account_tax.company_id.country_id.code != 'PE':
            account_tax.company_id = company_id
        if account_tax.invoice_repartition_line_ids and account_tax.refund_repartition_line_ids:
            for i in account_tax.invoice_repartition_line_ids:
                if i.repartition_type == 'tax':
                    i.account_id = new_account

            for i in account_tax.refund_repartition_line_ids:
                if i.repartition_type == 'tax':
                    i.account_id = new_account
        else:
            account_tax.sudo().write({
                'invoice_repartition_line_ids': [
                    (5, 0, 0),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base',
                    }),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': new_account,
                    }),
                ],
                'refund_repartition_line_ids': [
                    (5, 0, 0),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base',
                    }),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': new_account,
                    }),
                ]
            })

        account_tax = self.env.ref('ple_purchase_book.account_tax_ret_no_dom')
        new_account_1 = self.env['account.account'].search([('id', '=', self.env.ref('l10n_pe.chart6419').id)])
        new_account_2 = self.env['account.account'].search([('id', '=', self.env.ref('l10n_pe.chart40174').id)])
        if account_tax.company_id.country_id.code != 'PE':
            account_tax.company_id = company_id
        if account_tax.invoice_repartition_line_ids and account_tax.refund_repartition_line_ids:
            for i in account_tax.invoice_repartition_line_ids:
                if i.repartition_type == 'tax' and i.factor_percent == 100:
                    i.account_id = new_account_1
                if i.repartition_type == 'tax' and i.factor_percent == -100:
                    i.account_id = new_account_2

            for i in account_tax.refund_repartition_line_ids:
                if i.repartition_type == 'tax' and i.factor_percent == 100:
                    i.account_id = new_account_1
                if i.repartition_type == 'tax' and i.factor_percent == -100:
                    i.account_id = new_account_2
        else:
            account_tax.sudo().write({
                'invoice_repartition_line_ids': [
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base',
                    }),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': new_account_1,
                    }),
                    (0, 0, {
                        'factor_percent': -100,
                        'repartition_type': 'tax',
                        'account_id': new_account_2,
                    }),
                ],
                'refund_repartition_line_ids': [
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'base',
                    }),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': new_account_1,
                    }),
                    (0, 0, {
                        'factor_percent': -100,
                        'repartition_type': 'tax',
                        'account_id': new_account_2,
                    }),
                ]
            })
