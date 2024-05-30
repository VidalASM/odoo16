from odoo import fields, models, api


class PleBalanceInitial(models.Model):
    _name = 'ple.initial.balances.seveenten'
    _order = 'sequence asc'
    _description = 'ple initial balances seveenten'

    ple_report_inv_val_seventeen_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.seventeen',
        string='Reporte de Estado de Situación financiera'
    )

    trial_balances_catalog_id = fields.Many2one(
        string='Cuenta contable',
        comodel_name='trial.balances.catalog'
    )
    name = fields.Char(
        string='Nombre de la cuneta contable',
        compute='calculate_name'
    )
    debit = fields.Char(
        string='Debe',
    )
    credit = fields.Char(
        string='Haber',
    )
    sequence = fields.Integer(
        string='Sequencia',
    )

    def calculate_name(self):
        for rec in self:
            data = rec.trial_balances_catalog_id
            rec.name = data.name
            rec.sequence = data.sequence



    def calculate_name(self):
        for rec in self:
            data = rec.trial_balances_catalog_id
            rec.name = data.name
            rec.sequence = data.sequence


class PleTransferCancel(models.Model):
    _name = 'ple.transfers.cancellations'
    _description = 'ple ransfers cancellations'

    ple_report_inv_val_seventeen_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.seventeen',
        string='Reporte de Estado de Situación financiera'
    )
    transfers_cancellations_selection = fields.Selection(
        selection=[
            ('transfers', 'Transferencias'),
            ('cancellations', 'Cancelaciones'),
        ],
        string='Transferencias y cancelaciones '
    )
    trial_balances_catalog_id = fields.Many2one(
        string='Cuenta de balance de comprobación',
        comodel_name='trial.balances.catalog'
    )
    amount = fields.Char(
        string='Importe'
    )


class PleAdditionDeduction(models.Model):
    _name = 'ple.addition.deduction'
    _description = 'ple addition deduction'

    ple_report_inv_val_seventeen_id = fields.Many2one(
        comodel_name='ple.report.inv.bal.seventeen',
        string='Reporte de Estado de Situación financiera'
    )
    transfers_additions_selection = fields.Selection(
        selection=[
            ('additions', 'Adiciones'),
            ('deductions', 'Deducciones'),
        ],
        string='Adiciones y deducciones'
    )
    trial_balances_catalog_id = fields.Many2one(
        string='Cuenta de balance de comprobación',
        comodel_name='trial.balances.catalog'
    )
    amount = fields.Char(
        string='Importe'
    )
