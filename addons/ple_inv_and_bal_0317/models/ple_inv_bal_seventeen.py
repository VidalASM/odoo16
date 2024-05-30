from odoo import fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from ..reports.report_inv_bal_seventeen import ReportInvBalExcel, ReportInvBalTxt
import base64


class PleInvBalSeventeen(models.Model):
    _name = 'ple.report.inv.bal.seventeen'
    _description = '[3.17] Balance de comprobación'
    _inherit = 'ple.report.base'

    line_initial_balances_ids = fields.One2many(
        comodel_name='ple.initial.balances.seveenten',
        inverse_name='ple_report_inv_val_seventeen_id',
        string='Saldos iniciales'
    )
    line_transfers_cancellations_ids = fields.One2many(
        comodel_name='ple.transfers.cancellations',
        inverse_name='ple_report_inv_val_seventeen_id',
        string='Transferencias y cancelaciones'
    )
    line_additions_deductions_ids = fields.One2many(
        comodel_name='ple.addition.deduction',
        inverse_name='ple_report_inv_val_seventeen_id',
        string='Adiciones y deducciones'
    )

    txt_filename = fields.Char(string='Filaname .txt')
    txt_binary = fields.Binary(string='Reporte .TXT 3.17')
    pdf_filename = fields.Char(string='Filaname .PDF 3.17')
    pdf_binary = fields.Binary(string='Reporte .PDF 3.17')

    financial_statements_catalog = fields.Selection(
        selection=[
            ('01', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR DIVERSAS - INDIVIDUAL'),
            ('02', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR SEGUROS - INDIVIDUAL'),
            ('03', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR BANCOS Y FINANCIERAS - INDIVIDUAL'),
            ('04', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - ADMINISTRADORAS DE FONDOS DE PENSIONES (AFP)'),
            ('05', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - AGENTES DE INTERMEDIACIÓN'),
            ('06', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - FONDOS DE INVERSIÓN'),
            ('07', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - PATRIMONIO EN FIDEICOMISOS'),
            ('08', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - ICLV'),
            ('09', 'OTROS NO CONSIDERADOS EN LOS ANTERIORES')
        ],
        string='Catálogo estados financieros',
        default='09',
        required=True
    )
    eeff_presentation_opportunity = fields.Selection(
        selection=[
            ('01', 'Al 31 de diciembre'),
            ('02', 'Al 31 de enero, por modificación del porcentaje'),
            ('03', 'Al 30 de junio, por modificación del coeficiente o porcentaje'),
            ('04','Al último día del mes que sustentará la suspensión o modificación del coeficiente (distinto al 31 de enero o 30 de junio)'),
            ('05','Al día anterior a la entrada en vigencia de la fusión, escisión y demás formas de reorganización de sociedades o emperesas o extinción ''de la persona jurídica'),
            ('06', 'A la fecha del balance de liquidación, cierre o cese definitivo del deudor tributario'),
            ('07', 'A la fecha de presentación para libre propósito')
        ],
        string='Oportunidad de presentación de EEFF',
        required=True
    )

    def get_initial_movement_between_dates(self, date_start, company_id):
        movement_account_lines = dict()
        query = """
                SELECT
                    COALESCE(trial_balances.code,'')                            AS trial_code, 
                    trial_balances.id                                           AS trial_id,
                    SUM(account_move_line.debit)                                AS sum_debit,
                    SUM(account_move_line.credit)                               AS sum_credit,
                    SUM(account_move_line.balance)                              AS sum_balance
                FROM "account_move_line" AS "account_move_line"
                --  TYPE JOIN |  TABLE                         | VARIABLE                   | MATCH
                    LEFT JOIN  "account_account"				account_account				ON account_move_line.account_id=account_account.id
                    LEFT JOIN  "trial_balances_catalog"			trial_balances				ON account_account.trial_balances_catalog_id=trial_balances.id
                    LEFT JOIN  "account_move"		         	account_move				ON account_move_line.move_id=account_move.id
                    LEFT JOIN  "account_group"				    account_group				ON account_account.group_id=account_group.id
                -- FILTER QUERIES
                WHERE 
                    ("account_move_line"."date" < '{date_start}') 
                    AND (("account_move_line"."account_id" IN (
                        SELECT "account_account".id 
                        FROM "account_account" 
                        WHERE ("account_account"."account_type" IN (
                            SELECT "account_account".account_type 
                            FROM "account_account" 
                            WHERE ("account_account"."include_initial_balance" = True)))))) 
                                AND ("account_move_line"."company_id" = {company_id}) 
                                AND ("account_move"."state" = '{state}')
                                AND ("account_group"."code_prefix_start" !='89')
                -- GROUP DATA
                GROUP BY trial_balances.code,trial_balances.sequence,trial_balances.id
                ORDER BY trial_balances.sequence ASC;
                """.format(
            company_id=company_id.id,
            date_start=date_start,
            state='posted',
        )
        try:
            self.env.cr.execute(query)
            data_aml = self.env.cr.dictfetchall()
            for moves in data_aml:
                if moves['trial_id']:
                    movement_account_lines[moves['trial_code']] = {}
                    movement_account_lines[moves['trial_code']]['trial_id'] = moves['trial_id']
                    movement_account_lines[moves['trial_code']]['sum_debit'] = moves['sum_debit']
                    movement_account_lines[moves['trial_code']]['sum_credit'] = moves['sum_credit']
                    movement_account_lines[moves['trial_code']]['sum_balance'] = moves['sum_balance']
                else:
                    data_aml.remove(moves)
            return movement_account_lines
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')


    def get_movement_between_dates(self, date_start, date_end, company_id):
        movement_account_lines = dict()
        movement_account_lines_exceptions = dict()
        query = """
                SELECT
                    COALESCE(trial_balances.code,'')                            AS trial_code, 
                    trial_balances.id                                           AS trial_id,
                    account_move.journal_id                                     AS journal_id,
                    SUM(account_move_line.debit)                                AS sum_debit,
                    SUM(account_move_line.credit)                               AS sum_credit,
                    SUM(account_move_line.balance)                              AS sum_balance
                FROM "account_move_line" AS "account_move_line"
                --  TYPE JOIN |  TABLE                         | VARIABLE                   | MATCH
                    LEFT JOIN  "account_account"				account_account				ON account_move_line.account_id=account_account.id
                    LEFT JOIN  "trial_balances_catalog"			trial_balances				ON account_account.trial_balances_catalog_id=trial_balances.id
                    LEFT JOIN  "account_move"		         	account_move				ON account_move_line.move_id=account_move.id
                    LEFT JOIN  "account_group"				    account_group				ON account_account.group_id=account_group.id
                -- FILTER QUERIES
                WHERE 
                    ("account_move_line"."date" <= '{date_end}') AND 
                    ("account_move_line"."date" >= '{date_start}') AND
                    ("account_move_line"."company_id" = {company_id}) AND
                    ("account_move"."state" = '{state}')
                -- GROUP DATA
                GROUP BY trial_balances.code,trial_balances.sequence,trial_balances.id,account_move.journal_id
                ORDER BY trial_balances.sequence ASC;
                """.format(
            company_id=company_id.id,
            date_start=date_start,
            date_end=date_end,
            state='posted',
        )
        try:
            self.env.cr.execute(query)
            data_aml = self.env.cr.dictfetchall()
            journal_transferencias_id = self.env['account.journal'].search([('code', '=', 'TRANS')], limit=1).id
            journal_cancelaciones_id = self.env['account.journal'].search([('code', '=', 'CANCE')], limit=1).id
            for moves in data_aml:
                if moves['trial_id']:
                    movement_account_lines[moves['trial_code']] = []
                else:
                    data_aml.remove(moves)
            for moves in data_aml:
                for trial_code in movement_account_lines:
                        if trial_code == moves['trial_code']:
                            if moves['journal_id'] in [journal_transferencias_id, journal_cancelaciones_id]:
                                moves_exceptions = dict()
                                moves_exceptions = moves.copy()
                                movement_account_lines_exceptions[moves['trial_code']] = []
                                movement_account_lines_exceptions[trial_code].append(moves_exceptions)
                                moves['sum_debit'] = 0
                                moves['sum_credit'] = 0
                                moves['sum_balance'] = 0
                            movement_account_lines[trial_code].append(moves)
            return movement_account_lines, movement_account_lines_exceptions
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

    def action_generate_data_seventeen(self):
        data_initial_balances = self.get_lines_initial_balances()
        data_account_lines, data_account_lines_exceptions = self.get_movement_between_dates(self.date_start, self.date_end, self.company_id)
        data_transfer_cancellation = self.get_lines_transfer_cancellation()
        data_addition_deduction = self.get_lines_addition_deduction()

        trial_balances_query = """
           SELECT 
               id          as id_trial,
               code        as code_trial,
               name        as description_trial,
               sequence    as sequence_trial 
           FROM trial_balances_catalog 
           -- ORDER DATA
           ORDER BY sequence ASC;
       """
        self.env.cr.execute(trial_balances_query)
        val_trial_balances = self.env.cr.dictfetchall()

        val_result_losses = ['0', '1', '2', '3', '4', '5']
        val_result_balances = ['6', '7']
        trial_balances = []
        pdf_balances = []

        sum_total_initial_debit = 0
        sum_total_initial_credit = 0
        sum_total_movement_debit = 0
        sum_total_movement_credit = 0
        sum_total_higher_sum_credit = 0
        sum_total_balance_of_december_debtor = 0
        sum_total_active_balance_account = 0
        sum_total_passive_balance_account = 0
        sum_total_result_losses = 0
        sum_total_result_earnings = 0

        for val in val_trial_balances:
            is_empty = True
            sum_movement_debit = 0
            sum_movement_credit = 0
            sum_movement_debit_exceptions = 0
            sum_movement_credit_exceptions = 0

            validate_initial = val['code_trial'] in data_initial_balances
            validate_account_lines = val['code_trial'] in data_account_lines
            validate_account_lines_exceptions = val['code_trial'] in data_account_lines_exceptions
            validate_transfer = val['code_trial'] in data_transfer_cancellation
            validate_addition = val['code_trial'] in data_addition_deduction

            if validate_initial or validate_account_lines or validate_transfer or validate_addition:
                is_empty = False

            initial_balances = data_initial_balances.get(val['code_trial']) if validate_initial else dict()
            transfer_cancellation = data_transfer_cancellation.get(val['code_trial']) if validate_transfer else dict()
            addition_deduction = data_addition_deduction.get(val['code_trial']) if validate_addition else dict()            

            initial_debit = initial_balances['init_debit'] if validate_initial else 0
            initial_credit = initial_balances['init_credit'] if validate_initial else 0

            if validate_account_lines_exceptions:
                for account_lines_exceptions in data_account_lines_exceptions[val['code_trial']]:
                    movement_debit_exceptions = account_lines_exceptions['sum_debit'] if validate_account_lines_exceptions else 0
                    movement_credit_exceptions = account_lines_exceptions['sum_credit'] if validate_account_lines_exceptions else 0
                    sum_movement_debit_exceptions += movement_debit_exceptions
                    sum_movement_credit_exceptions += movement_credit_exceptions
                transfer_cancellation_debit = sum_movement_debit_exceptions
                transfer_cancellation_credit = sum_movement_credit_exceptions
            else:
                transfer_cancellation_debit = transfer_cancellation['amount_transf'] if 'amount_transf' in transfer_cancellation else 0
                transfer_cancellation_credit = transfer_cancellation['amount_cancel'] if 'amount_cancel' in transfer_cancellation else 0

            addition = addition_deduction['amount_addition'] if 'amount_addition' in addition_deduction else 0
            deduction = addition_deduction['amount_deduct'] if 'amount_deduct' in addition_deduction else 0

            if validate_account_lines:
                for account_lines in data_account_lines[val['code_trial']]:
                    movement_debit = account_lines['sum_debit'] if validate_account_lines else 0
                    movement_credit = account_lines['sum_credit'] if validate_account_lines else 0
                    sum_movement_debit += movement_debit
                    sum_movement_credit += movement_credit

            higher_sum_debit = sum_movement_debit + initial_debit
            higher_sum_credit = sum_movement_credit + initial_credit

            balance_of_december_debtor = abs(higher_sum_debit - higher_sum_credit) if higher_sum_debit - higher_sum_credit >= 0 else 0
            balance_of_december_creditor = abs(higher_sum_debit - higher_sum_credit) if higher_sum_debit - higher_sum_credit < 0 else 0

            condition_one = balance_of_december_debtor - balance_of_december_creditor + transfer_cancellation_debit - transfer_cancellation_credit

            active_balance_account = abs(condition_one) if val['code_trial'][0] in val_result_losses and condition_one >= 0 else 0
            passive_balance_account = abs(condition_one) if val['code_trial'][0] in val_result_losses and condition_one < 0 else 0

            result_losses = abs(condition_one) if val['code_trial'][0] in val_result_balances and condition_one >= 0 else 0
            result_earnings = abs(condition_one) if val['code_trial'][0] in val_result_balances and condition_one < 0 else 0

            sum_total_initial_debit += initial_debit
            sum_total_initial_credit += initial_credit
            sum_total_movement_debit += sum_movement_debit
            sum_total_movement_credit += sum_movement_credit
            sum_total_higher_sum_credit += higher_sum_credit
            sum_total_balance_of_december_debtor += balance_of_december_debtor
            sum_total_active_balance_account += active_balance_account
            sum_total_passive_balance_account += passive_balance_account
            sum_total_result_losses += result_losses
            sum_total_result_earnings += result_earnings

            if not is_empty:
                value = {
                    'period': self.date_end.strftime('%Y%m%d'),
                    'code': val['code_trial'],
                    'initial_debit': initial_debit,
                    'initial_credit': initial_credit,
                    'movement_debit': sum_movement_debit,
                    'movement_credit': sum_movement_credit,
                    'higher_sum_debit': higher_sum_debit,
                    'higher_sum_credit': higher_sum_credit,
                    'balance_of_december_debtor': balance_of_december_debtor,
                    'balance_of_december_creditor': balance_of_december_creditor,
                    'transfer_cancellation_debit': transfer_cancellation_debit,
                    'transfer_cancellation_credit': transfer_cancellation_credit,
                    'active_balance_account': round(active_balance_account, 2),
                    'passive_balance_account': round(passive_balance_account, 2),
                    'result_losses': result_losses,
                    'result_earnings': result_earnings,
                    'addition': addition,
                    'deduction': deduction,
                    'state': 1,
                    'name': val['description_trial'],
                    'sequence': val['sequence_trial'],
                    'id_trial': val['id_trial'],
                }
                trial_balances.append(value)

                value_pdf = {
                    'code': val['code_trial'],
                    'name': val['description_trial'],
                    'initial_debit': '{:.2f}'.format(initial_debit),
                    'initial_credit': '{:.2f}'.format(initial_credit),
                    'movement_debit': '{:.2f}'.format(sum_movement_debit),
                    'movement_credit': '{:.2f}'.format(sum_movement_credit),
                    'higher_sum_credit': '{:.2f}'.format(higher_sum_credit),
                    'higher_sum_debit': '{:.2f}'.format(higher_sum_debit),
                    'balance_of_december_debtor': '{:.2f}'.format(balance_of_december_debtor),
                    'active_balance_account': '{:.2f}'.format(active_balance_account),
                    'passive_balance_account': '{:.2f}'.format(passive_balance_account),
                    'result_losses': '{:.2f}'.format(result_losses),
                    'result_earnings': '{:.2f}'.format(result_earnings),
                }
                pdf_balances.append(value_pdf)
        
        condition_two = sum_total_result_earnings - sum_total_result_losses

        exercise_active_account = abs(condition_two) if condition_two >= 0 else 0.00
        exercise_passive_account = abs(condition_two) if condition_two < 0 else 0.00
        exercise_result_losses = abs(condition_two) if condition_two >= 0 else 0.00
        exercise_result_earnings = abs(condition_two) if condition_two < 0 else 0.00

        total_active_balance_account = sum_total_active_balance_account + exercise_active_account
        total_passive_balance_account = sum_total_passive_balance_account + exercise_passive_account
        total_result_losses = sum_total_result_losses + exercise_result_losses
        total_result_earnings = sum_total_result_earnings + exercise_result_earnings

        report_xls = ReportInvBalExcel(self, trial_balances)
        report_txt = ReportInvBalTxt(self, trial_balances)

        values_content_xls = report_xls.get_content()
        values_content = report_txt.get_content()

        data = {
            'txt_binary': base64.b64encode(values_content.encode() or '\n'.encode()),
            'txt_filename': report_txt.get_filename(),
            'error_dialog': 'No hay contenido para presentar en el registro de ventas electrónicos de este periodo.' if not values_content else False,
            'xls_binary': base64.b64encode(values_content_xls),
            'xls_filename': report_xls.get_filename(),
            'date_ple': fields.Date.today(),
            'state': 'load'
        }
        self.write(data)
        report_name = "ple_inv_and_bal_0317.action_print_status_finance_seventeen"
        datos = {
            'values_lines': pdf_balances,
            'sum_initial_debit': '{:.2f}'.format(sum_total_initial_debit),
            'sum_initial_credit': '{:.2f}'.format(sum_total_initial_credit),
            'sum_movement_debit': '{:.2f}'.format(sum_total_movement_debit),
            'sum_movement_credit': '{:.2f}'.format(sum_total_movement_credit),
            'sum_higher_sum_credit': '{:.2f}'.format(sum_total_higher_sum_credit),
            'sum_balance_of_december_debtor': '{:.2f}'.format(sum_total_balance_of_december_debtor),
            'sum_active_balance_account': '{:.2f}'.format(sum_total_active_balance_account),
            'sum_passive_balance_account': '{:.2f}'.format(sum_total_passive_balance_account),
            'sum_result_losses': '{:.2f}'.format(sum_total_result_losses),
            'sum_result_earnings': '{:.2f}'.format(sum_total_result_earnings),
            'exercise_active_account': '{:.2f}'.format(exercise_active_account),
            'exercise_passive_account': '{:.2f}'.format(exercise_passive_account),
            'exercise_result_losses': '{:.2f}'.format(exercise_result_losses),
            'exercise_result_earnings': '{:.2f}'.format(exercise_result_earnings),
            'total_active_balance_account': '{:.2f}'.format(total_active_balance_account),
            'total_passive_balance_account': '{:.2f}'.format(total_passive_balance_account),
            'total_result_losses': '{:.2f}'.format(total_result_losses),
            'total_result_earnings': '{:.2f}'.format(total_result_earnings),
        }

        pdf = self.env.ref(report_name)._render_qweb_pdf('ple_inv_and_bal_0317.print_status_finance_seventeen', res_ids=self.id, data=datos)[0]
        self.pdf_binary = base64.encodebytes(pdf)
        year, month, day = self.date_end.strftime('%Y/%m/%d').split('/')
        self.pdf_filename = f'Libro_Balance_Comprobación_{year}{month}.pdf'

    def action_generate_initial_balances_317(self):
        date_start = self.date_start

        self.write({
            'line_initial_balances_ids': [(5, 0, 0)],
        })
        
        data_account_lines = self.get_initial_movement_between_dates(date_start, self.company_id)
        
        for initial_val in data_account_lines.keys():
            data = data_account_lines.get(initial_val)
            debit = data['sum_balance'] if data['sum_balance'] > 0 else 0.0
            credit = data['sum_balance'] if data['sum_balance'] < 0 else 0.0
            self.write({
                'line_initial_balances_ids': [
                    (0, 0, {
                        'trial_balances_catalog_id': data['trial_id'],
                        'debit': debit,
                        'credit': abs(credit),
                        'ple_report_inv_val_seventeen_id': self.id
                    })
                ]
            })

    def get_lines_initial_balances(self):
        values = dict()
        init_data = self.line_initial_balances_ids
        for data in init_data:
            code = data.trial_balances_catalog_id.code
            values[code] = {}
            values[code]['init_debit'] = float(data.debit)
            values[code]['init_credit'] = float(data.credit)
        return values

    def get_lines_transfer_cancellation(self):
        values = dict()
        init_data = self.line_transfers_cancellations_ids
        for data in init_data:
            code = data.trial_balances_catalog_id.code
            type_doc = data.transfers_cancellations_selection
            if code in values:
                if type_doc == 'transfers':
                    if 'amount_transf' in values[code]:
                        values[code]['amount_transf'] += float(data.amount)
                    else:
                        values[code]['amount_transf'] = float(data.amount)
                else:
                    if 'amount_cancel' in values[code]:
                        values[code]['amount_cancel'] += float(data.amount)
                    else:
                        values[code]['amount_cancel'] = float(data.amount)
            else:
                values[code] = {}
                if type_doc == 'transfers':
                    values[code]['amount_transf'] = float(data.amount)
                else:
                    values[code]['amount_cancel'] = float(data.amount)
        return values

    def get_lines_addition_deduction(self):
        values = dict()
        init_data = self.line_additions_deductions_ids
        for data in init_data:
            code = data.trial_balances_catalog_id.code
            type_doc = data.transfers_additions_selection
            if code in values:
                if type_doc == 'additions':
                    if 'amount_addition' in values[code]:
                        values[code]['amount_addition'] += float(data.amount)
                    else:
                        values[code]['amount_addition'] = float(data.amount)
                else:
                    if 'amount_deduct' in values[code]:
                        values[code]['amount_deduct'] += float(data.amount)
                    else:
                        values[code]['amount_deduct'] = float(data.amount)
            else:
                values[code] = {}
                if type_doc == 'additions':
                    values[code]['amount_addition'] = float(data.amount)
                else:
                    values[code]['amount_deduct'] = float(data.amount)
        return values

    def action_close(self):
        self.write({'state': 'closed'})

    def action_rollback(self):
        self.write({'state': 'draft'})
        self.write({'line_initial_balances_ids': [(5, 0, 0)]})
        self.write({
            'txt_binary': False,
            'txt_filename': False,
            'xls_binary': False,
            'xls_filename': False,
            'pdf_binary': False,
            'pdf_filename': False,
        })