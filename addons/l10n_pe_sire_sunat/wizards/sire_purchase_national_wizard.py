import base64
import zipfile

from io import BytesIO

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from ..reports.sire_purchase_accept_proposed import SirePurchaseAcceptProposedXlsx, SirePurchaseAcceptProposedTxt
from ..reports.sire_purchase_replace_proposed import SirePurchaseReplaceProposedXlsx, SirePurchaseReplaceProposedTxt
from ..reports.sire_purchase_subsequent_adjustments import SirePurchaseSubsequentAdjustmentsXlsx, SirePurchaseSubsequentAdjustmentsTxt
from ..reports.sire_purchase_general_format import SirePurchaseGeneralFormatXlsx, SirePurchaseGeneralFormatTxt


class SirePurchaseNationalWizard(models.TransientModel):
    _name = 'sire.purchase.national.wizard'
    _inherit = 'sire.purchase.base'
    _description = 'Sire Purchase National Wizard'

    state_send = fields.Selection(
        selection=[
            ('0', '[0] Cierre de operaciones - Bajo de inscripciones en el RUC'),
            ('1', '[1] Empresa o entidad operativa'),
            ('2', '[2] Cierre de libro - No obligado a llevarlo')
        ],
        string='Estado de envío',
        required=True
    )
    opportunity_code = fields.Selection(
        selection=[
            ('01', '[01] RCE - Cuando acepta la propuesta'),
            ('02', '[02] RCE - Cuando reemplaza la propuesta'),
            ('03', '[03] RCE - Cuando realiza ajustes posteriores'),
            ('04', '[04] Reporte de ajustes posteriores de periodos anteriores al nuevo sistema de registros - Formato general')
        ],
        string='Código de oportunidad',
        required=True
    )
    correlative = fields.Char(string='Correlativo')

    @api.onchange('opportunity_code')
    def _onchange_opportunity_code(self):
        if self.correlative:
            self.correlative = ''

    def _where_sire_purchase(self):
        return super()._where_sire_purchase() + """
            AND (
                account_move.is_nodomicilied IS NULL
                OR account_move.is_nodomicilied = false
            )
        """

    def _generate_xlsx_file(self, processed_results):
        if self.opportunity_code == '01':
            xlsx_report = SirePurchaseAcceptProposedXlsx(self, processed_results)
        elif self.opportunity_code == '02':
            xlsx_report = SirePurchaseReplaceProposedXlsx(self, processed_results)
        elif self.opportunity_code == '03':
            xlsx_report = SirePurchaseSubsequentAdjustmentsXlsx(self, processed_results)
        elif self.opportunity_code == '04':
            xlsx_report = SirePurchaseGeneralFormatXlsx(self, processed_results)
        else:
            raise ValidationError('Por favor, se necesita un código de oportunidad para generar el reporte, gracias.')
        return {
            'xlsx_content': xlsx_report.get_content(),
            'xlsx_filename': xlsx_report.get_filename()
        }

    def _generate_txt_file(self, processed_results):
        if self.opportunity_code == '01':
            txt_report = SirePurchaseAcceptProposedTxt(self, processed_results)
        elif self.opportunity_code == '02':
            txt_report = SirePurchaseReplaceProposedTxt(self, processed_results)
        elif self.opportunity_code == '03':
            txt_report = SirePurchaseSubsequentAdjustmentsTxt(self, processed_results)
        elif self.opportunity_code == '04':
            txt_report = SirePurchaseGeneralFormatTxt(self, processed_results)
        else:
            raise ValidationError('Por favor, se necesita un código de oportunidad para generar el reporte, gracias.')
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

    def _return_view_sire_purchase(self):
        wizard_form_id = self.env.ref('l10n_pe_sire_sunat.sire_purchase_national_wizard_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sire.purchase.national.wizard',
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
        return self._return_view_sire_purchase()
