import markupsafe

from odoo import fields, models, _
from odoo.tools import config


class AccountReportLine(models.Model):
    _inherit = "account.report.line"

    eeff_ple_ids = fields.Many2one(
        'eeff.ple',
        string='3.1 Rubro ESF'
    )


class AccountReport(models.Model):
    _inherit = "account.report"

    allow_txt_generation = fields.Selection(
        selection_add=[('01', '3.1 Estado de situación financiera')]
    )

    def open_wizard_txt_report_ple_3_1(self, options):
        self.ensure_one()
        new_wizard = self.env['wizard.report.txt.ple.3.1'].create({'report_id': self.id})
        view_id = self.env.ref('ple_inv_and_bal_0301_ee.view_wizard_report_txt_ple_3_1').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generar TXT 3.1'),
            'view_mode': 'form',
            'res_model': 'wizard.report.txt.ple.3.1',
            'target': 'new',
            'res_id': new_wizard.id,
            'views': [[view_id, 'form']],
        }

    def _get_options(self, previous_options=None):
        options = super(AccountReport, self)._get_options(previous_options)
        if self.allow_txt_generation == '01':
            options['change_header'] = True
            options['buttons'].append({
                'name': _('EXPORTAR A TXT'),
                'sequence': 30,
                'action': 'open_wizard_txt_report_ple_3_1'
            })
        return options

    def export_to_pdf(self, options):
        if self.allow_txt_generation != '01':
            return super(AccountReport, self).export_to_pdf(options)
        
        if not config['test_enable']:
            self = self.with_context(commit_assetsbundle=True)

        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.company,
        }

        print_mode_self = self.with_context(print_mode=True)
        print_options = print_mode_self._get_options(previous_options=options)
        body_html = print_mode_self.get_html(print_options, self._filter_out_folded_children(print_mode_self._get_lines(print_options)))
        body = self.env['ir.ui.view']._render_template(
            "account_reports.print_template",
            values=dict(rcontext, body_html=body_html),
        )
        body_string = str(body)
        special_header = self.env['ir.actions.report']._render_qweb_html('ple_inv_and_bal_0301_ee.action_report_header_ple_3_1', self.id)[0]
        body_string = body_string.replace('<body class="o_account_reports_body_print">', '<body class="o_account_reports_body_print">' + special_header.decode())
        body = markupsafe.Markup(body_string)
        
        footer = self.env['ir.actions.report']._render_template("web.internal_layout", values=rcontext)
        footer = self.env['ir.actions.report']._render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=markupsafe.Markup(footer.decode())))

        landscape = False
        if len(print_options['columns']) * len(print_options['column_groups']) > 5:
            landscape = True

        file_content = self.env['ir.actions.report']._run_wkhtmltopdf(
            [body],
            footer=footer.decode(),
            landscape=landscape,
            specific_paperformat_args={
                'data-report-margin-top': 10,
                'data-report-header-spacing': 10,
                'data-report-margin-bottom': 15,
            }
        )

        return {
            'file_name': self.get_default_report_filename('pdf'),
            'file_content': file_content,
            'file_type': 'pdf',
        }
