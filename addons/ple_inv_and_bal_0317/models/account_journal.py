from odoo import fields, models, api

value_trans = {'name': 'Transferencias - 3.17 Inventarios y Balances',
               'type': 'general',
               'code': 'TRANS'}

value_cance = {'name': 'Cancelaciones - 3.17 Inventarios y Balances',
               'type': 'general',
               'code': 'CANCE'}

value_adici = {'name': 'Adiciones - 3.17 Inventarios y Balances',
               'type': 'general',
               'code': 'ADICI'}

value_deduc = {'name': 'Deducciones - 3.17 Inventarios y Balances',
               'type': 'general',
               'code': 'DEDUC'}


class PleInvBalSeventeen(models.Model):
    _inherit = 'account.journal'

    @api.model
    def generate_account_journal(self):

        journal = self.search([('code', '=', 'TRANS')], limit=1)
        journal.update(value_trans) if journal else self.create(value_trans)

        journal = self.search([('code', '=', 'CANCE')], limit=1)
        journal.update(value_cance) if journal else self.create(value_cance)

        journal = self.search([('code', '=', 'ADICI')], limit=1)
        journal.write(value_adici) if journal else self.create(value_adici)

        journal = self.search([('code', '=', 'DEDUC')], limit=1)
        journal.write(value_deduc) if journal else self.create(value_deduc)

