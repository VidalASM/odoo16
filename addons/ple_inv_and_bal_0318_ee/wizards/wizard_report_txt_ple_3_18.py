import base64
import time

from odoo import models, fields

from ..reports.report_txt_ple_3_18 import ReportTXTPLE


# TODO: delete after updates
class WizardReportTxtPLEOld(models.Model):
    _name = 'wizard.report.ple.18.ee.generate.txt'
    _description = 'Wizard Report TXT PLE 3.18 Old'


class WizardReportTxtPLE(models.TransientModel):
    _name = 'wizard.report.txt.ple.3.18'
    _description = 'Wizard Report TXT PLE 3.18'

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
    state_send = fields.Selection(selection=[
        ('0', 'Cierre de Operaciones - Bajo de Inscripciones en el RUC'),
        ('1', 'Empresa o Entidad Operativa'),
        ('2', 'Cierre de libro - No Obligado a llevarlo')
    ], required=True,
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
    txt_binary = fields.Binary(string='Reporte .TXT 3.18')

    def contains_code(self, list, filter):
        for i in range(0, len(list)):
            if filter(list[i]):
                return i
        return -1

    def obtain_dict_data(self):
        data_txt_dict = []
        move_lines = self.env['account.move.line'].search([('journal_id.type', 'in', ('bank', 'cash'))])
        for move_line in move_lines:
            account_id = move_line.account_id
            if account_id.account_type != 'asset_cash':
                for efemdcat in account_id.efemd_category:
                    temp_index = self.contains_code(data_txt_dict, lambda x:x['code'] == efemdcat.code )
                    if len(data_txt_dict) > 0 and temp_index != -1:
                        data_txt_dict[temp_index]['balance'] += move_line.balance * (-1)
                    elif efemdcat.code != False:
                        data_txt_dict.append({
                            'code': efemdcat.code,
                            'hierarchy': 'HIJO',
                            'balance': move_line.balance * (-1),
                            'parent_code': efemdcat.parent_ids[0].code,
                            'grandparent_code': efemdcat.parent_ids[0].parent_ids[0].code if efemdcat.parent_ids[0].parent_ids[0].code else '',
                            'greatgrandparent_code': efemdcat.parent_ids[0].parent_ids[0].parent_ids[0].code if efemdcat.parent_ids[0].parent_ids[0].parent_ids[0].code else ''
                        })
        return data_txt_dict

    def flatten_tree(self, node, result_list):
        result_list.append({
            'code': node['code'],
            'hierarchy': 'PADRE E HIJO A LA VEZ',
            'balance': node['balance'],
            'parent_code': '',
            'grandparent_code': '',
        })
        for child in node['children']:
            self.flatten_tree(child, result_list)

    def add_parent_childrens(self, data_txt_dict):
        parent_nodes = {}

        for entry in data_txt_dict:
            parent_code = entry['parent_code']
            grandparent_code = entry['grandparent_code']
            greatgrandparent_code = entry['greatgrandparent_code']

            for code in [parent_code, grandparent_code, greatgrandparent_code]:
                if code:
                    if code not in parent_nodes:
                        parent_nodes[code] = {
                            'code': code,
                            'hierarchy': 'PADRE E HIJO A LA VEZ',
                            'balance': 0,
                            'children': []
                        }

        for entry in data_txt_dict:
            child_node = {
                'code': entry['code'],
                'hierarchy': 'PADRE E HIJO A LA VEZ',
                'balance': entry['balance'],
                'children': []
            }

            if entry['greatgrandparent_code']:
                parent_nodes[entry['greatgrandparent_code']]['children'].append(child_node)
            elif entry['grandparent_code']:
                parent_nodes[entry['grandparent_code']]['children'].append(child_node)
            elif entry['parent_code']:
                parent_nodes[entry['parent_code']]['children'].append(child_node)

            for code in [entry['parent_code'], entry['grandparent_code'], entry['greatgrandparent_code']]:
                if code:
                    parent_nodes[code]['balance'] += entry['balance']

        top_level_nodes = [node for node in parent_nodes.values() if node['code'] not in data_txt_dict]

        result_list = []
        for node in top_level_nodes:
            self.flatten_tree(node, result_list)

        res_list = result_list[::-1]
        return res_list

    def generate_318_data_txt(self, rpl):
        data_txt_dict = self.obtain_dict_data()
        data_txt_dict = self.add_parent_childrens(data_txt_dict)
        filter_rpl = [line for line in rpl if 'level' in line and line['level'] == 0]
        if len(filter_rpl) >= 3:
            data_txt_dict.append({'code': '3D0405', 'hierarchy': 'PADRE TOTAL', 'balance': filter_rpl[1]['columns'][0]['name'][3:].replace(',', '')})
            data_txt_dict.append({'code': '3D0402', 'hierarchy': 'SIN PADRE', 'balance': filter_rpl[0]['columns'][0]['name'][3:].replace(',', '')})
            data_txt_dict.append({'code': '3D04ST', 'hierarchy': 'SIN PADRE', 'balance': filter_rpl[-1]['columns'][0]['name'][3:].replace(',', '')})
        return data_txt_dict

    def generate_data(self):
        data_dict = dict()
        report = self.env.ref('ple_inv_and_bal_0318_ee.ple_inv_bal_3_18_report')
        options = report._get_options()

        options['date']['date_from'] = self.date_start.strftime('%Y-%m-%d')
        options['date']['date_to'] = self.date_end.strftime('%Y-%m-%d')

        report_lines = report._get_lines(options)
        data_txt_dict = self.generate_318_data_txt(report_lines)

        for line in report_lines:
            if line['name'][0].isdigit():
                code = line['name'].split(' ')[0]
                line_id = self.env['account.account'].search([('code', '=', code)], limit=1)
                if line_id.efemd_category.code == False:
                    data_dict[line_id.efemd_category.code] = []
        for line in report_lines:
            if line['name'][0].isdigit():
                code = line['name'].split(' ')[0]
                line_id = self.env['account.account'].search([('code', '=', code)], limit=1)
                balance = line['columns'][0]['name'][3:].replace(',', '')
                for code_line in data_dict:
                    if code_line == line_id.efemd_category.code:
                        data_dict[code_line].append({
                            'period': self.date_end.strftime('%Y%m%d'),
                            'code': self.financial_statements_catalog,
                            'balance_rubro_cont': balance,
                            'data_txt_dict': data_txt_dict,
                            'indicador': '1',
                        })
        return data_dict

    def action_return_wizard(self):
        view_id = self.env.ref('ple_inv_and_bal_0318_ee.view_wizard_report_txt_ple_3_18').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.report.txt.ple.3.18',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'res_id': self.id,
            'target': 'new'
        }

    def action_generate_txt(self):
        self.ensure_one()
        data = self.generate_data()
        report_18_ee = ReportTXTPLE(self, data)
        data = {
            'txt_binary': base64.b64encode(report_18_ee.get_content().encode() or '\n'.encode()),
            'txt_filename': report_18_ee.get_filename(),
        }
        self.write(data)
        return self.action_return_wizard()
