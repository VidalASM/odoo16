from . import models
from . import reports
from odoo import api, SUPERUSER_ID


def _link_tags_ids(cr, register):
    env = api.Environment(cr, SUPERUSER_ID, {})

    def generate_tag_id(name):
        return env['account.account.tag'].search([('name', '=', '%s' % name)], limit=1)

    def set_tag_ids(account_tax, first, second):
        if first:
            if account_tax.repartition_type == 'base':
                account_tax.write({'tag_ids': [(4, generate_tag_id(first).id)]})
        if second:
            if account_tax.repartition_type == 'tax':
                account_tax.write({'tag_ids': [(4, generate_tag_id(second).id)]})

    type_acc = ['igv_18', 'igv_18_included', 'exo', 'ina', 'exp']
    tags_invoices = ['+S_BASE_OG', '+S_TAX_OG', '+S_BASE_OE', '+S_BASE_OU', '+S_BASE_EXP']
    tags_invoices_corrective = ['-S_BASE_OG', '-S_TAX_OG', '-S_BASE_OE', '-S_BASE_OU', '-S_BASE_EXP']
    for rec in type_acc:
        try:
            account = env.ref('l10n_pe.1_sale_tax_%s' % rec)
            if rec == 'igv_18':
                for acc_tax in account.invoice_repartition_line_ids:
                    set_tag_ids(acc_tax, tags_invoices[0], tags_invoices[1])
                for acc_tax in account.refund_repartition_line_ids:
                    set_tag_ids(acc_tax, tags_invoices_corrective[0], tags_invoices_corrective[1])
            elif rec == 'igv_18_included':
                for acc_tax in account.invoice_repartition_line_ids:
                    set_tag_ids(acc_tax, tags_invoices[0], tags_invoices[1])
                for acc_tax in account.refund_repartition_line_ids:
                    set_tag_ids(acc_tax, tags_invoices_corrective[0], tags_invoices_corrective[1])
            elif rec == 'exo':
                for acc_tax in account.invoice_repartition_line_ids:
                    set_tag_ids(acc_tax, tags_invoices[2], False)
                for acc_tax in account.refund_repartition_line_ids:
                    set_tag_ids(acc_tax, tags_invoices_corrective[2], False)
            elif rec == 'ina':
                for acc_tax in account.invoice_repartition_line_ids:
                    set_tag_ids(acc_tax, tags_invoices[3], False)
                for acc_tax in account.refund_repartition_line_ids:
                    set_tag_ids(acc_tax, tags_invoices_corrective[3], False)
            elif rec == 'exp':
                for acc_tax in account.invoice_repartition_line_ids:
                    set_tag_ids(acc_tax, tags_invoices[4], False)
                for acc_tax in account.refund_repartition_line_ids:
                    set_tag_ids(acc_tax, tags_invoices_corrective[4], False)
        except:
            pass
