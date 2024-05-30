from datetime import datetime
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    years = [('{}'.format(i), '{}'.format(i)) for i in range(1981, datetime.today().year + 1)]

    year_aduana = fields.Selection(
        string='Año Emisión',
        selection=years,
        help='Año de emisión de la Declaración Aduanera de Mercancías - Importación '
             'definitiva o de la Despacho Simplificado - Importación Simplificada'
    )
    code_aduana = fields.Many2one(
        string='Dependencia Aduanera',
        comodel_name='code.aduana'
    )

    @api.onchange('l10n_latam_document_type_id')
    def _onchange_l10n_latam_document_type_id(self):
        super(AccountMove, self)._onchange_l10n_latam_document_type_id()
        if self.move_type not in ['out_invoice', 'out_refund'] and self.l10n_latam_document_type_id.code not in ['50', '52']:
            self.code_aduana = False
            self.year_aduana = ''

    @api.constrains('error_dialog', 'move_type')
    def _constrains_error_dialog(self):
        for rec in self:
            if rec.move_type in ['in_invoice', 'in_refund'] and rec.error_dialog and rec.l10n_latam_document_type_id.code not in ['50', '52']:
                raise ValidationError('Debe resolver las siguientes requerimientos antes de guardar: \n %s' % rec.error_dialog)
