from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def subtotal(self):
        subtotal = 0
        for i in self.invoice_line_ids:
            if i.product_id:
                subtotal += (i.quantity * i.account_value_unit)
        return subtotal

    def total_discount(self):
        sum_disc = 0
        for i in self.invoice_line_ids:
            if i.product_id:
                if i.tax_ids and i.tax_ids[0].tax_group_id.l10n_pe_edi_code == 'IGV':
                    sum_disc += (i.account_value_unit * i.quantity * (i.discount / 100))
                else:
                    sum_disc = 0
            else:
                sum_disc = 0
        return sum_disc

    def taxes_efact(self):
        sum_IGV = 0
        sum_INA = 0
        sum_EXO = 0
        sum_GRAT = 0
        sum_EXP = 0
        data = []
        for i in self.invoice_line_ids:
            if i.product_id:
                if i.tax_ids and i.tax_ids[0].tax_group_id.l10n_pe_edi_code == 'IGV':
                    sum_IGV += (i.account_value_unit * i.quantity)
                if i.tax_ids and i.tax_ids[0].tax_group_id.l10n_pe_edi_code == 'INA':
                    sum_INA += (i.account_value_unit * i.quantity)
                if i.tax_ids and i.tax_ids[0].tax_group_id.l10n_pe_edi_code == 'EXO':
                    sum_EXO += (i.account_value_unit * i.quantity)
                if i.tax_ids and i.tax_ids[0].tax_group_id.l10n_pe_edi_code == 'EXP':
                    sum_EXP += (i.account_value_unit * i.quantity)
                if i.tax_ids and i.tax_ids[0].tax_group_id.l10n_pe_edi_code == 'GRA':
                    sum_GRAT += (i.quantity * i.price_unit)

        data.append([sum_IGV, sum_INA, sum_EXO, sum_EXP, sum_GRAT])
        return data

    def efact1(self):
        data = self.taxes_efact()
        return data[0][0]

    def efact2(self):
        data = self.taxes_efact()
        return data[0][1]

    def efact3(self):
        data = self.taxes_efact()
        return data[0][2]

    def efact4(self):
        data = self.taxes_efact()
        return data[0][3]

    def efact5(self):
        data = self.taxes_efact()
        return data[0][4]

    def resdays(self):
        if self.invoice_date:
            num_days = self.invoice_date_due - self.invoice_date
        else:
            num_days = self.invoice_date_due
        return num_days.days


class Sale(models.Model):
    _inherit = 'sale.order'
