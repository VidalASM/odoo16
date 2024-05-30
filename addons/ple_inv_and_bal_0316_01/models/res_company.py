from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    lines_report_0316 = fields.One2many(comodel_name='report.ple.031601.fields',
                                        inverse_name='company_id')
    is_member_indicator = fields.Boolean(string='Indicador',
                                         compute='_compute_is_member_indicator',
                                         default=False)

    @api.depends('lines_report_0316')
    def _compute_is_member_indicator(self):

        for line_company in self:
            line_company.is_member_indicator = False
            for line_report in line_company.lines_report_0316:
                if line_report.is_member:
                    line_company.is_member_indicator = True
                    break


class Company(models.Model):
    _name = 'report.ple.031601.fields'

    company_id = fields.Many2one(comodel_name='res.company')

    social_reason = fields.Many2one(string='Apellidos y Nombres del socio o razón social',
                                    comodel_name='res.partner')
    identification_number = fields.Char(string='Número de identificación fiscal',
                                        related='social_reason.vat')
    document_type = fields.Many2one(string='Tipo de documento de identidad',
                                    comodel_name='l10n_latam.identification.type',
                                    related='social_reason.l10n_latam_identification_type_id')

    partition_type_code = fields.Selection(
        [
            ('01', 'Acciones con derecho a voto'),
            ('02', 'Acciones sin derecho a voto'),
            ('03', 'Participaciones'),
            ('04', 'Otros'),
        ],
        string='Código de los tipos de acciones o participaciones')
    participations_number = fields.Char(string='Número de acciones o de participaciones sociales')
    participations_percentage = fields.Float(string='Porcentaje de participaciones sociales o acciones')
    is_member = fields.Boolean('¿Es socio actualmente?', default=False)
    date_incorporation_partner = fields.Date(string='Fecha de incorporación del socio')
