import base64
import zipfile

from io import BytesIO

from odoo import models, fields, api
from odoo.exceptions import UserError

from ..reports.sire_purchase_complements_rate import SirePurchaseComplementsRateTxt


class SirePurchaseComplementsRateWizard(models.TransientModel):
    _name = 'sire.purchase.complements.rate.wizard'
    _inherit = 'sire.purchase.base'
    _description = 'Sire Purchase Complements Rate Wizard'

    year = fields.Selection(readonly=True)
    month = fields.Selection(readonly=True)
    correlative = fields.Char(string='Correlativo', required=True)
    rate_ids = fields.Many2many('res.currency.rate', string='Tasas')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get('active_model') == 'res.currency.rate':
            rate_ids = self.env['res.currency.rate'].browse(self._context.get('active_ids', []))
            if not rate_ids:
                raise UserError('No se han seleccionado tasas para validar.')

            first_move_date = rate_ids[0].name
            first_move_month = first_move_date.month
            first_move_year = first_move_date.year

            for rate in rate_ids:
                rate_date = rate.name
                if rate_date.month != first_move_month or rate_date.year != first_move_year:
                    raise UserError('No todas las tasas seleccionadas son del mismo mes y año.')

            res['rate_ids'] = [(6, 0, rate_ids.ids)]
            res['month'] = str(first_move_month).zfill(2)
            res['year'] = str(first_move_year)
        else:
            raise UserError('Este wizard solo puede ser llamado desde registros del modelo res.currency.rate.')
        return res

    def _generate_txt_file(self, processed_results):
        txt_report = SirePurchaseComplementsRateTxt(self, processed_results)
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
        processed_results = list()
        for rate in self.rate_ids:
            processed_results.append({
                'period': "{}{}".format(self.year, self.month),
                'date': rate.name.strftime("%d/%m/%Y"),
                'currency_name': rate.currency_id.name,
                'inverse_company_rate':  "{:.3f}".format(rate.inverse_company_rate)
            })
        txt_values = self._generate_txt_file(processed_results)
        zip_values = self._generate_zip_file(txt_values.get('txt_filename'), txt_values.get('txt_content', '\n'))
        return {
            'txt_values': txt_values,
            'zip_values': zip_values
        }

    def _save_generate_files(self, file_values):
        has_content_values = file_values['txt_values'].get('txt_content', False)
        error_dialog = 'No hay contenido que presentar para este periodo.' if not has_content_values else ''
        self.write({
            'zip_binary': file_values['zip_values'].get('zip_binary'),
            'zip_filename': file_values['zip_values'].get('zip_filename'),
            'error_dialog': error_dialog,
        })

    def _return_view_sire_purchase(self):
        wizard_form_id = self.env.ref('l10n_pe_sire_sunat.sire_purchase_complements_rate_wizard_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sire.purchase.complements.rate.wizard',
            'views': [(wizard_form_id, 'form')],
            'view_id': wizard_form_id,
            'res_id': self.id,
            'target': 'new'
        }

    def action_generate_files(self):
        self.write({'zip_binary': False, 'zip_filename': ''})
        file_values = self._generate_files()
        self._save_generate_files(file_values)
        return self._return_view_sire_purchase()
