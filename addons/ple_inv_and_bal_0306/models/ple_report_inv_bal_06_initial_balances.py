from odoo import fields, models
from odoo.exceptions import ValidationError

from datetime import datetime

from dateutil.relativedelta import relativedelta


class PleReportInvBal06InitialBalances(models.Model):
    _inherit = 'ple.report.inv.bal.06'

    line_initial_ids = fields.One2many(
        comodel_name='ple.inv.bal.line.initial.balances.06',
        inverse_name='ple_report_inv_val_06_id',
        string='Líneas iniciales'
    )
    line_final_ids = fields.One2many(
        comodel_name='ple.inv.bal.line.final.balances.06',
        inverse_name='ple_report_inv_val_06_id',
        string='Líneas finales'
    )

    def action_generate_initial_whit_ending_balances(self):
        data = False
        documents = self.env['ple.report.inv.bal.06'].search(
            [
                ('date_start', '>=', self.date_start - relativedelta(years=1)),
                ('date_end', '<=', self.date_start),
                ('company_id', '=', self.company_id.id),
                ('state', 'in', ('load', 'closed')),
            ],
            limit=1
        )
        if documents:
            data = True
            self.write({'line_initial_ids': [(5, 0, 0)]})
            for obj_line in documents.line_final_ids:
                self.write({
                    'line_initial_ids': [
                        (0, 0, {
                            'name': obj_line.name,
                            'document_name': obj_line.document_name,
                            'correlative': obj_line.correlative,
                            'type_document_debtor': obj_line.type_document_debtor,
                            'tax_identification_number': obj_line.tax_identification_number,
                            'business_name': obj_line.business_name,
                            'type_document': obj_line.type_document,
                            'number_serie': obj_line.number_serie,
                            'number_document': obj_line.number_document,
                            'date_of_issue': obj_line.date_of_issue,
                            'provisioned_invoice': obj_line.provisioned_invoice,
                            'provision_amount': obj_line.provision_amount,
                            'state': obj_line.state,
                            'ple_report_inv_val_06_id': self.id,
                        }),
                    ]
                })
        return data

    def action_generate_initial_balances(self):
        self.line_initial_ids.unlink()

        query = """
            SELECT 
                account.id
            FROM account_account AS account
            INNER JOIN account_group AS account_group ON account.group_id = account_group.id
            WHERE 
                account_group.code_prefix_start = '19' and 
                account_group.code_prefix_end = '19'                  
        """

        try:
            self.env.cr.execute(query)
            val_account = self.env.cr.dictfetchall()
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la query, comunicar al administrador: \n {error}')

        if not val_account:
            self.write({'error_dialog': 'No hay cuentas configuradas con Prefijo de código 19'})
            return True

        accounts = []
        for i in val_account:
            accounts.append(i['id'])

        query = """
            SELECT
                LEFT('{period}', 8) as name,

                LEFT(COALESCE(REPLACE(REPLACE(REPLACE(move.name, '/', ''), '-', ''), ' ', ''), ''), 40) as document_name,
                
                LEFT(COALESCE(move_line.ple_correlative, ''), 10) as correlative,
                
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(identification_type_move_doubtful.l10n_pe_vat_code, '')
                ELSE COALESCE(identification_type.l10n_pe_vat_code, '') 
                END, 1) AS type_document_debtor,
                
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(partner_move_doubtful.vat, '') 
                ELSE COALESCE(partner.vat, '') 
                END, 15) AS tax_identification_number,
                            
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(partner_move_doubtful.name, '') 
                ELSE COALESCE(partner.name, '') 
                END, 100) AS business_name,
                
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(document_type_move_doubtful.code, '00') 
                ELSE COALESCE(SPLIT_PART(move_line.name, '.', 1), '00') 
                END, 2) AS type_document,
                
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(SPLIT_PART(REPLACE(move_doubtful.name, ' ', ''), '-', 1), '')
                ELSE COALESCE(SPLIT_PART(move_line.name, '.', 2), '')
                END, 24) AS number_serie,
                
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                THEN COALESCE(SPLIT_PART(REPLACE(move_doubtful.name, ' ', ''), '-', 2), '')
                ELSE COALESCE(SPLIT_PART(move_line.name, '.', 3), '')
                END, 20) AS number_document,
            
                LEFT(CASE WHEN move_doubtful.id IS NOT NULL 
                    THEN COALESCE(TO_CHAR(move_doubtful.invoice_date, 'DD/MM/YYYY'), '')
                    ELSE COALESCE(SPLIT_PART(move_line.name, '.', 4), '')
                END, 10) AS date_of_issue,
                                
                CASE WHEN move_doubtful.id IS NOT NULL 
                THEN move_doubtful.id
                ELSE move.id 
                END AS provisioned_invoice,
                
                UDF_numeric_char(sum(move_line.balance)) as provision_amount,
                
                {ple_report_inv_val_06_id} as ple_report_inv_val_06_id
                            
            FROM account_move_line                    AS move_line
            INNER JOIN account_move                   AS move                              ON move_line.move_id = move.id
            INNER JOIN account_account                AS account                           ON move_line.account_id = account.id
            INNER JOIN account_group                  AS account_group                     ON account.group_id = account_group.id
            LEFT JOIN res_partner                     AS partner                           ON move_line.partner_id = partner.id
            LEFT JOIN l10n_latam_identification_type  AS identification_type               ON partner.l10n_latam_identification_type_id = identification_type.id
            LEFT JOIN account_move                    AS move_doubtful                     ON move.invoice_doubtful_accounts = move_doubtful.id
            LEFT JOIN res_partner                     AS partner_move_doubtful             ON move_doubtful.partner_id = partner_move_doubtful.id
            LEFT JOIN l10n_latam_identification_type  AS identification_type_move_doubtful ON partner_move_doubtful.l10n_latam_identification_type_id = identification_type_move_doubtful.id
            LEFT JOIN l10n_latam_document_type        AS document_type_move_doubtful       ON move_doubtful.l10n_latam_document_type_id = document_type_move_doubtful.id
            
            WHERE 
                account_group.code_prefix_start = '19' AND 
                account_group.code_prefix_end = '19' AND
                move_line.date >= '{date_start}' AND 
                move_line.date <= '{date_end}' AND 
                move_line.company_id = {company_id} AND
                move.state = '{state}' AND
                move_line.account_id in {accounts}
            
            GROUP BY
                document_name, 
                correlative, 
                type_document_debtor, 
                tax_identification_number,
                business_name, 
                type_document, 
                number_serie,
                number_document,
                date_of_issue,
                provisioned_invoice
        """.format(
            period=self.date_end.strftime('%Y%m%d'),
            ple_report_inv_val_06_id=self.id,
            date_start=self.date_start - relativedelta(years=1),
            date_end=self.date_end - relativedelta(years=1),
            company_id=self.company_id.id,
            state='posted',
            accounts=tuple(accounts)
        )
        
        try:
            self.env.cr.execute(query)
            values = self.env.cr.dictfetchall()
            for dict in values:
                dict.setdefault('state', '1')
            lines_report = list(values)
            self.env['ple.inv.bal.line.initial.balances.06'].create(lines_report)
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la query, comunicar al administrador: \n {error}')

    def action_generate_initial_balances_306(self):
        data = self.action_generate_initial_whit_ending_balances()
        if data:
            pass
        else:
            self.action_generate_initial_balances()
        return

    def capture_initial_balances_id(self):
        quantity_hand = dict()
        for obj in self.line_initial_ids:
            quantity_hand[obj.provisioned_invoice] = {}
            quantity_hand[obj.provisioned_invoice]['name'] = obj.name
            quantity_hand[obj.provisioned_invoice]['document_name'] = obj.document_name
            quantity_hand[obj.provisioned_invoice]['correlative'] = obj.correlative
            quantity_hand[obj.provisioned_invoice]['type_document_debtor'] = obj.type_document_debtor
            quantity_hand[obj.provisioned_invoice]['tax_identification_number'] = obj.tax_identification_number
            quantity_hand[obj.provisioned_invoice]['business_name'] = obj.business_name
            quantity_hand[obj.provisioned_invoice]['type_document'] = obj.type_document
            quantity_hand[obj.provisioned_invoice]['number_serie'] = obj.number_serie
            quantity_hand[obj.provisioned_invoice]['number_document'] = obj.number_document
            quantity_hand[obj.provisioned_invoice]['date_of_issue'] = obj.date_of_issue
            quantity_hand[obj.provisioned_invoice]['provisioned_invoice'] = obj.provisioned_invoice
            quantity_hand[obj.provisioned_invoice]['provision_amount'] = obj.provision_amount
            quantity_hand[obj.provisioned_invoice]['state'] = obj.state
        return quantity_hand


class PleInvBalLineInitialBalances06(models.Model):
    _name = 'ple.inv.bal.line.initial.balances.06'
    _description = 'Ple Inv Bal Line Initial Balances 06'
    _order = 'name desc'

    name = fields.Char(string='Periodo')
    document_name = fields.Char(string='CUO')
    correlative = fields.Char(string='Correlative')
    type_document_debtor = fields.Char(string='Tipo de documento del deudor')
    tax_identification_number = fields.Char(string='Número de documento del deudor')
    business_name = fields.Char(string='Razon social del deudor')
    type_document = fields.Char(string='Tipo de CPE de la cuenta por cobrar')
    number_serie = fields.Char(string='Número de serie del comprobante de pago')
    number_document = fields.Char(string='Número del comprobante de pago')
    date_of_issue = fields.Char(string='Fecha de emisión del comprobante de pago')
    provisioned_invoice = fields.Char(string='Factura provisionada')
    provision_amount = fields.Float(string='Monto de la provisión')
    state = fields.Char(string='Indica el estado de la operación')
    ple_report_inv_val_06_id = fields.Many2one(comodel_name='ple.report.inv.bal.06', string='Reporte PLE 0306')


class PleInvBalLineFinalBalances06(models.Model):
    _name = 'ple.inv.bal.line.final.balances.06'
    _description = 'Ple Inv Bal Line Final Balances 06'
    _order = 'name desc'

    name = fields.Char(string='Periodo')
    document_name = fields.Char(string='CUO')
    correlative = fields.Char(string='Correlativo')
    type_document_debtor = fields.Char(string='Tipo de documento del deudor')
    tax_identification_number = fields.Char(string='Número de documento deudor')
    business_name = fields.Char(string='Razon social del deudor')
    type_document = fields.Char(string='Tipo de CPE de la cuenta por cobrar')
    number_serie = fields.Char(string='Número de serie del comprobante de pago')
    number_document = fields.Char(string='Número del comprobante de pago')
    date_of_issue = fields.Char(string='Fecha de emisión del comprobante de pago')
    provisioned_invoice = fields.Char(string='Factura provisionada')
    provision_amount = fields.Float(string='Monto de la provisión')
    state = fields.Char(string='Indica el estado de la operación')
    ple_report_inv_val_06_id = fields.Many2one(comodel_name='ple.report.inv.bal.06', string='Reporte PLE 0306')
