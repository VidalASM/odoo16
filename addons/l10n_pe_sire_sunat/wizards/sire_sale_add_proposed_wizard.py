import base64
import zipfile

from io import BytesIO

from odoo import models, fields, api
from odoo.exceptions import UserError

from ..reports.sire_sale_add_proposed import SireSaleAddProposedXlsx, SireSaleAddProposedTxt


class SireSaleAddProposedWizard(models.TransientModel):
    _name = 'sire.sale.add.proposed.wizard'
    _inherit = 'sire.sale.base'
    _description = 'Sire Sale Add Proposed Wizard'

    year = fields.Selection(readonly=True)
    month = fields.Selection(readonly=True)
    correlative = fields.Char(string='Correlativo', required=True)
    move_ids = fields.Many2many('account.move', string='Movimientos')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get('active_model') == 'account.move':
            move_ids = self.env['account.move'].browse(self._context.get('active_ids', []))
            if not move_ids:
                raise UserError('No se han seleccionado movimientos para validar.')

            first_move_date = move_ids[0].date
            first_move_month = first_move_date.month
            first_move_year = first_move_date.year

            for move in move_ids:
                move_date = move.date
                if move_date.month != first_move_month or move_date.year != first_move_year:
                    raise UserError('No todos los movimientos seleccionados son del mismo mes y año.')

            res['move_ids'] = [(6, 0, move_ids.ids)]
            res['month'] = str(first_move_month).zfill(2)
            res['year'] = str(first_move_year)
        else:
            raise UserError('Este wizard solo puede ser llamado desde registros del modelo account.move.')
        return res

    def _where_sire_sale(self):
        if len(self.move_ids.ids) == 1:
            return f"""
                account_move.id = {self.move_ids.ids[0]}
            """
        return f"""
            account_move.id in {tuple(self.move_ids.ids)}
        """

    def _generate_xlsx_file(self, processed_results):
        xlsx_report = SireSaleAddProposedXlsx(self, processed_results)
        return {
            'xlsx_content': xlsx_report.get_content(),
            'xlsx_filename': xlsx_report.get_filename()
        }

    def _generate_txt_file(self, processed_results):
        txt_report = SireSaleAddProposedTxt(self, processed_results)
        return {
            'txt_content': txt_report.get_content(),
            'txt_filename': txt_report.get_filename()
        }

    def _generate_zip_file(self, txt_filename, txt_content):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr(txt_filename, txt_content.encode())
        zip_binary = base64.b64encode(zip_buffer.getvalue())
        zip_filename = '{}.zip'.format(txt_filename.split('.')[0])
        return {
            'zip_binary': zip_binary,
            'zip_filename': zip_filename
        }

    def _generate_files(self):
        processed_results = self._process_query_results()
        xlsx_values = self._generate_xlsx_file(processed_results)
        txt_values = self._generate_txt_file(processed_results)
        zip_values = self._generate_zip_file(txt_values.get('txt_filename'), txt_values.get('txt_content', '\n'))
        return {
            'xlsx_values': xlsx_values,
            'txt_values': txt_values,
            'zip_values': zip_values
        }

    def _save_generate_files(self, file_values):
        has_content_values = file_values['txt_values'].get('txt_content', False)
        error_dialog = 'No hay contenido que presentar para este periodo.' if not has_content_values else ''
        self.write({
            'xlsx_binary': base64.b64encode(file_values['xlsx_values'].get('xlsx_content')),
            'xlsx_filename': file_values['xlsx_values'].get('xlsx_filename'),
            'zip_binary': file_values['zip_values'].get('zip_binary'),
            'zip_filename': file_values['zip_values'].get('zip_filename'),
            'error_dialog': error_dialog,
        })

    def _return_view_sire_sale(self):
        wizard_form_id = self.env.ref('l10n_pe_sire_sunat.sire_sale_add_proposed_wizard_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sire.sale.add.proposed.wizard',
            'views': [(wizard_form_id, 'form')],
            'view_id': wizard_form_id,
            'res_id': self.id,
            'target': 'new'
        }

    def action_generate_files(self):
        self.write({
            'xlsx_binary': False,
            'xlsx_filename': '',
            'zip_binary': False,
            'zip_filename': ''
        })
        file_values = self._generate_files()
        self._save_generate_files(file_values)
        return self._return_view_sire_sale()
