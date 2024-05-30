import base64
import time

from odoo import models, fields

from ..reports.report_txt_ple_3_1 import ReportTXTPLE


# TODO: delete after updates
class WizardReportTxtPLEOld(models.TransientModel):
    _name = 'wizard.report.generate.0301.ee'
    _description = 'Wizard Report TXT PLE 3.1 Old'


class WizardReportTxtPLE(models.TransientModel):
    _name = 'wizard.report.txt.ple.3.1'
    _description = 'Wizard Report TXT PLE 3.1'

    report_id = fields.Integer(
        string='Parent Report Id', 
        required=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    date_start = fields.Date(
        string='Fecha inicio',
        required=True,
        default=lambda *date_start: time.strftime('%Y-01-01')
    )
    date_end = fields.Date(
        string='Fecha fin',
        required=True,
        default=lambda *date_end: time.strftime('%Y-12-31')
    )
    state_send = fields.Selection(
        selection=[
            ('0', 'Cierre de Operaciones - Bajo de Inscripciones en el RUC'),
            ('1', 'Empresa o Entidad Operativa'),
            ('2', 'Cierre de libro - No Obligado a llevarlo')
        ], 
        required=True,
        string='Estado de envío',
        default='0'
    )
    date_ple = fields.Date(
        string='Generado el',
        required=True,
        default=lambda date_ple: fields.Date.context_today(date_ple),
        readonly=True
    )
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
        required=True,
    )
    eeff_presentation_opportunity = fields.Selection(
        selection=[
            ('01', 'Al 31 de diciembre'),
            ('02', 'Al 31 de enero, por modificación del porcentaje'),
            ('03', 'Al 30 de junio, por modificación del coeficiente o porcentaje'),
            ('04', 'Al último día del mes que sustentará la suspensión o modificación del coeficiente (distinto al 31 de enero o 30 de junio)'),
            ('05', 'Al día anterior a la entrada en vigencia de la fusión, escisión y demás formas de reorganización de sociedades o empresas o extinción de la persona jurídica'),
            ('06', 'A la fecha del balance de liquidación, cierre o cese definitivo del deudor tributario'),
            ('07', 'A la fecha de presentación para libre propósito')
        ],
        string='Oportunidad de presentación de EEFF',
        required=True,
        default='01'
    )
    txt_filename = fields.Char(string='Filaname .txt')
    txt_binary = fields.Binary(string='Reporte .TXT 3.1')
    
    def action_generate_report_txt_ple(self):
        esf_report = self.env['account.report'].browse(self.report_id)
        esf_options = self._get_report_options(esf_report)
        
        pre_report_lines = self._prepare_report_lines(esf_report, esf_options)        
        pro_report_lines = self._process_report_lines(pre_report_lines)
        
        sorted_pro_report_lines = sorted(pro_report_lines, key=lambda line: line['sequence'])
        report_lines = self._get_report_lines(sorted_pro_report_lines)
        
        report_txt_ple = ReportTXTPLE(self, report_lines)
        data = {
            'txt_binary': base64.b64encode(report_txt_ple.get_content().encode() or '\n'.encode()),
            'txt_filename': report_txt_ple.get_filename(),
        }
        self.write(data)
        return self.action_return_wizard()
    
    def _get_report_options(self, esf_report):
        options = esf_report._get_options()
        options['date']['date_from'] = self.date_start.strftime('%Y-%m-%d')
        options['date']['date_to'] = self.date_end.strftime('%Y-%m-%d')
        return options

    def _prepare_report_lines(self, esf_report, esf_options):
        pre_report_lines = []

        esf_report_lines = esf_report._get_lines(esf_options)
        
        for esf_report_line in esf_report_lines:
            model, line_id = esf_report._parse_line_id(esf_report_line.get('id'))[-1][1:]
            
            if model != 'account.report.line':
                continue

            report_line = self.env['account.report.line'].browse(line_id)

            if report_line.eeff_ple_ids and report_line.eeff_ple_ids.eeff_type == '3.1':
                pre_report_lines.append({
                    'sequence': report_line.eeff_ple_ids.sequence,
                    'period': self.date_end.strftime('%Y%m%d'),
                    'catalog_code': self.financial_statements_catalog,
                    'esf_ple_id': report_line.eeff_ple_ids.id,
                    'parent_id': report_line.eeff_ple_ids.id,
                    'financial_code': report_line.eeff_ple_ids.code,
                    'balance': esf_report_line['columns'][0]['no_format'],
                    'state': 1
                })

        return pre_report_lines

    def _process_report_lines(self, pre_report_lines):
        dict_report_lines = {}
        
        for pre_report_line in pre_report_lines:
            self._check_key_in_dicts(pre_report_line['esf_ple_id'], dict_report_lines, pre_report_line)
            self._check_parent_lines(pre_report_line['parent_id'], pre_report_line['balance'], dict_report_lines)
        
        pro_report_lines = list(dict_report_lines.values())
        for pro_report_line in pro_report_lines:
            if len(pro_report_line) == 10:
                del pro_report_line['parent_id']
        
        return pro_report_lines

    def _check_key_in_dicts(self, key_val, dict_data, new_dict_data):
        if key_val not in dict_data.keys():
            dict_data.setdefault(key_val, new_dict_data)
        else:
            new_credit = float(dict_data[key_val]['balance']) + float(new_dict_data['balance'])
            dict_data[key_val]['balance'] = self.env['ple.report.base'].check_decimals(new_credit)
    
    def _check_parent_lines(self, esf_ple_id, balance, dict_data):
        if isinstance(esf_ple_id, int):
            eeff_ple_id = self.env['eeff.ple'].search([('id', '=', esf_ple_id)], limit=1)
        else:
            eeff_ple_id = esf_ple_id
        
        parent_ids = eeff_ple_id.parent_ids
        
        if not parent_ids:
            return
        
        for parent_id in parent_ids:
            parent_values = {
                'sequence': parent_id.sequence,
                'period': self.date_end.strftime('%Y%m%d'),
                'catalog_code': self.financial_statements_catalog,
                'esf_ple_id': parent_id.id,
                'parent_id': parent_id.id,
                'financial_code': parent_id.code,
                'balance': balance,
                'state': '1',
            }
            self._check_key_in_dicts(parent_id.id, dict_data, parent_values)
            self._check_parent_lines(parent_id, balance, dict_data)

    def _get_report_lines(self, sorted_pro_report_lines):
        report_lines = [
            {
                'period': sorted_pro_report_line['period'],
                'catalog_code': sorted_pro_report_line['catalog_code'],
                'financial_code': sorted_pro_report_line['financial_code'],
                'balance': 0.0 if round(float(sorted_pro_report_line['balance']), 2) == -0.0 else round(float(sorted_pro_report_line['balance']), 2),
                'state': sorted_pro_report_line['state'],
            }
            for sorted_pro_report_line in sorted_pro_report_lines
        ]
        return report_lines

    def action_return_wizard(self):
        view_id = self.env.ref('ple_inv_and_bal_0301_ee.view_wizard_report_txt_ple_3_1').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.report.txt.ple.3.1',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'res_id': self.id,
            'target': 'new'
        }
