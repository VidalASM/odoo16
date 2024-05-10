from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.model
    def _get_supported_account_types(self):
        return [('bank', 'Normal'), ('wage', 'Sueldo'), ('cts', 'CTS'), ('other', 'Otros')]

    acc_type = fields.Selection(
        selection=lambda x: x.env['res.partner.bank'].get_supported_account_types(),
        default='bank',
        string='Type',
        help='Bank account type: Normal or IBAN. Inferred from the bank account number.',
        compute=False,
        required=False
    )
    type_bank_code = fields.Char(string='Código')
    cci = fields.Char(string='CCI')


class HrEmployeeTypeBankAccount(models.Model):
    _inherit = 'hr.employee'

    account_salary_bank = fields.Char(string='Cuenta Sueldo', readonly=True, compute='_select_information_partner')
    type_salary_bank = fields.Char(string='Banco Sueldo', readonly=True, compute='_select_information_partner')
    account_cts_bank = fields.Char(string='Cuenta CTS', readonly=True, compute='_select_information_partner')
    type_cts_bank = fields.Char(string='Banco CTS', readonly=True, compute='_select_information_partner')

    def _select_information_partner(self):
        for employee in self:
            res_partner_bank = employee.env['res.partner.bank'].search([('partner_id.name', '=', employee.address_home_id.name)])
            account_salary_bank_employee = ''
            type_salary_bank_employee = ''
            account_cts_bank_employee = ''
            type_cts_bank_employee = ''
            for res in res_partner_bank:
                if res.acc_type == 'wage':
                    account_salary_bank_employee = res.acc_number
                    type_salary_bank_employee = res.bank_id.name
                if res.acc_type == 'cts':
                    account_cts_bank_employee = res.acc_number
                    type_cts_bank_employee = res.bank_id.name
            for result in employee:
                if account_salary_bank_employee != '':
                    result.account_salary_bank = account_salary_bank_employee
                else:
                    result.account_salary_bank = ''
                if type_salary_bank_employee != '':
                    result.type_salary_bank = type_salary_bank_employee
                else:
                    result.type_salary_bank = ''
                if account_cts_bank_employee != '':
                    result.account_cts_bank = account_cts_bank_employee
                else:
                    result.account_cts_bank = ''
                if type_cts_bank_employee != '':
                    result.type_cts_bank = type_cts_bank_employee
                else:
                    result.type_cts_bank = ''
