from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    igv_withholding_indicator = fields.Boolean(
        string='Indicador de retención del IGV o Renta en Compras',
        help='Si el campo se activa, de forma automática aparece el en registro de compras'
             ' que el comprobante de pago registrado está afecto a retención del IGV, Renta o ambas inclusive'
    )
    bool_pay_invoice = fields.Char(
        string='Indicador de comprobante de pago cancelado'
    )
    inv_id = fields.Many2one(
        string='C. P. Sustento',
        comodel_name='account.move',
        domain=[('state', 'not in', ['draft', 'cancel'])]
    )
    inv_type_document = fields.Many2one(
        comodel_name='l10n_latam.document.type',
        string='Tipo documento',
        help='Tipo de Comprobante de Pago o Documento que sustenta el crédito fiscal.'
    )
    inv_serie = fields.Char(
        string='Serie de Comprabante',
        help='Serie del comprobante de pago o documento que sustenta el crédito fiscal.'
             'En los casos de la Declaración Única de Aduanas (DUA) o de la '
             'Declaración Simplificada de Importación (DSI) se consignará el código de la dependencia Aduanera.'
    )
    inv_correlative = fields.Char(
        string='Correlativo de Comprobante',
        help='Número del comprobante de pago o documento o número de orden del formulario físico o virtual'
             ' donde conste el pago del impuesto, tratándose de la utilización de servicios prestados por'
             ' no domiciliados u otros, número de la DUA o de la DSI, que sustente el crédito fiscal.'
    )
    inv_year_dua_dsi = fields.Char(
        string='Año emisión  DUA o DSI',
        size=4,
        help='Año de emisión de la DUA o DSI que sustenta el crédito fiscal. Odoo valida que en este campo se '
             'registre número mayor a  1981 y menor o igual al año del periodo informado'
    )
    inv_retention_igv = fields.Float(
        string='Monto retención de IGV',
        digits=(12, 2),
        help='Monto de retención del IGV'
    )
    is_nodomicilied = fields.Boolean(
        string='No Domiciliado',
        compute='_compute_is_nodomicilied',
        store=True,
        readonly=False,
    )
    linkage_id = fields.Many2one(
        comodel_name='link.economic',
        string='Vinculación',
        help='Vínculo entre el contribuyente y el residente en el extranjero.'
             'Se completan de acuerdo a la tabla 27 del Anexo 2 de SUNAT.'
    )
    hard_rent = fields.Float(
        string='Renta Bruta',
        digits=(12, 2)
    )
    deduccion_cost = fields.Float(
        string='Deducción/Costo',
        digits=(12, 2),
    )
    neto_rent = fields.Float(
        string='Renta Neta',
        digits=(12, 2)
    )
    retention_rate = fields.Float(
        string='Tasa de Retención',
        digits=(3, 2),
    )
    tax_withheld = fields.Float(
        string='Impuesto retenido',
        digits=(12, 2)
    )
    cdi = fields.Selection(
        string='CDI',
        selection=[
            ("00", "NINGUNO"),
            ("01", "CANADA"),
            ("02", "CHILE"),
            ("03", "COMUNIDAD ANDINA DE NACIONES (CAN)"),
            ("04", "BRASIL"),
            ("05", "ESTADOS UNIDOS MEXICANOS"),
            ("06", "REPUBLICA DE COREA"),
            ("07", "CONFEDERACIÓN SUIZA"),
            ("08", "PORTUGAL"),
            ("09", "OTROS")
        ],
        help='Convenios para evitar la doble imposición.'
             'Es campo se autocompleta con el campo “Código de Convenio para evitar doble imposición”.'
             'Se completan de acuerdo a la tabla 25 del Anexo 2 de SUNAT.'
    )
    exoneration_nodomicilied_id = fields.Many2one(
        comodel_name='exoneration.nodomicilied',
        string='Exoneracion de No Domiciliado'
    )
    type_rent_id = fields.Many2one(
        comodel_name='type.rent',
        string='Tipo de Renta'
    )
    taken_id = fields.Many2one(
        string='Modalidad de servicio prestado',
        comodel_name='service.taken'
    )
    application_article = fields.Char(
        string='Aplicación Art. 76°',
        help='Consignar 1 si aplica, sino se queda en Blanco. '
             '(Aplicación del penúltimo párrafo del Art. 76° de la Ley del Impuesto a la Renta)'
    )

    types_goods_services_id = fields.Many2one(
        comodel_name='classification.services',
        string='Clasificación de los bienes y servicios adquiridos'
    )

    @api.depends('company_id', 'partner_id')
    def _compute_is_nodomicilied(self):
        for obj in self:
            if obj.partner_id and obj.company_id.country_id == self.env.ref('base.pe'):
                if obj.partner_id.country_id and obj.partner_id.country_id == obj.company_id.country_id:
                    obj.is_nodomicilied = False
                elif not obj.partner_id.country_id:
                    obj.is_nodomicilied = False
                else:
                    obj.is_nodomicilied = True


    @api.model_create_multi
    def create(self, values):
        r = super(AccountMove, self).create(values)
        for move in r:
            if move.move_type in ['out_invoice', 'out_refund']:
                move.ple_state = '1'
            elif move.move_type in ['in_invoice', 'in_refund']:
                zero_taxes = 0
                for line in move.invoice_line_ids:
                    for tax in line.tax_ids:
                        if tax.amount == 0.00:
                            zero_taxes += 1

                if move.is_nodomicilied or zero_taxes == len(move.invoice_line_ids):
                    move.ple_state = '0'
                elif move.ple_date and move.invoice_date and move.invoice_date.month < move.ple_date.month or (
                        move.invoice_date and move.invoice_date.year < move.ple_date.year):
                    move.ple_state = '6'
                else:
                    move.ple_state = '1'
        return r

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('form'):
            tags = [('field', 'is_nodomicilied'), ('field', 'bool_pay_invoice')]
            arch, view = self.env['res.partner']._tags_invisible_per_country(arch, view, tags, [self.env.ref('base.pe')])
        return arch, view

    @api.onchange('date')
    def onchange_ple_date_from_date(self):
        self.ple_date = self.date
        self.validation_ple_state()

    @api.onchange('invoice_date')
    def onchange_date_from_invoice_date(self):
        if self.invoice_date:
            self.date = self.invoice_date
            self.validation_ple_state()

    @api.onchange('invoice_line_ids')
    def onchange_invoice_line_ids_validation_ple(self):
        if self.invoice_line_ids:
            self.validation_ple_state()

    def validation_ple_state(self):
        taxes_diff = 0
        for line in self.invoice_line_ids:
            for tax in line.tax_ids:
                if tax.amount == 0.00:
                    taxes_diff += 1
        if self.is_nodomicilied or taxes_diff == len(self.invoice_line_ids):
            self.ple_state = '0'
        elif self.invoice_date and self.date:
            if self.invoice_date.month < self.date.month or self.invoice_date.year < self.date.year:
                self.ple_state = '6'
            else:
                self.ple_state = '1'
        else:
            self.ple_state = '1'

    @api.onchange('invoice_line_ids', 'l10n_latam_document_type_id')
    def nodomicilied_fields_update(self):

        fiscal_position_name = self.partner_id.property_account_position_id.name
        country_res = self.partner_id.country_id
        doc_type = self.l10n_latam_document_type_id
        ret_no_domi_30 = self.env['account.tax'].search([('name', '=', '30% RET. NO DOMICILIADO')], limit=1).id
        ret_no_domi_18 = self.env['account.tax'].search([('name', '=', '18% NO DOMICILIADO')], limit=1).id

        # --- First Case
        cond11 = country_res.code != "pe"
        cond12 = fiscal_position_name in ('NO DOMICILIADO SIN CDI', "NO DOMICILIADO CON CDI")
        cond14 = doc_type.code == '91'
        cond15 = False

        for line in self.invoice_line_ids:
            tax_ids = line.tax_ids.ids
            if ret_no_domi_30 in tax_ids or ret_no_domi_18 in tax_ids:
                cond15 = True
                break

        # --- Second Case
        cond21 = cond11
        cond22 = fiscal_position_name == "IMPORTACIONES"
        cond24 = cond14

        account_type_dict = dict(self.env['account.account']._fields['account_type']._description_selection(self.env))

        if cond11 and cond12 and self.is_nodomicilied and cond14 and cond15:

            # Monto de retencion de igv
            move_line_ret_igv = None
            for line in self.line_ids:
                if account_type_dict[line.account_id.account_type] == 'Activos Circulantes':
                    move_line_ret_igv = line
                    break

            self.inv_retention_igv = move_line_ret_igv.debit if move_line_ret_igv else 0.00

            # Renta bruta
            move_line_hard_rent = None
            for line in self.line_ids:
                if account_type_dict[line.account_id.account_type] == 'Por pagar':
                    move_line_hard_rent = line
                    break

            self.hard_rent = move_line_hard_rent.credit if move_line_hard_rent else 0.00

            # Renta neta
            self.neto_rent = self.hard_rent - self.deduccion_cost

            if fiscal_position_name == "NO DOMICILIADO SIN CDI":
                # Tasa de retención

                self.retention_rate = 0.00
                for line in self.invoice_line_ids:
                    if ret_no_domi_30 in line.tax_ids.ids:
                        self.retention_rate = 30.00
                        break

                # Impuesto Retenido
                move_line_ret = None
                for line in self.line_ids:
                    if account_type_dict[line.account_id.account_type] == 'Pasivos Circulantes' and line.account_id.code[:5] == '40174':
                        move_line_ret = line
                        break

                self.tax_withheld = move_line_ret.credit if move_line_ret else 0.00

            elif fiscal_position_name == "NO DOMICILIADO CON CDI":
                # Tasa de retención
                ret_nodom_tag_id = self.env['account.tax'].search([('name', '=', '30% RET. NO DOMICILIADO')],
                                                                  limit=1).id

                for line in self.invoice_line_ids:
                    if ret_nodom_tag_id in line.tax_ids.ids:
                        self.hard_rent = 0.00
                        self.neto_rent = 0.00
                        break

                self.retention_rate = 0.00

                # Impuesto Retenido
                self.tax_withheld = 0.00

        elif cond21 and cond22 and self.is_nodomicilied and cond24:
            move_line_hard_rent = None
            for line in self.line_ids:
                if account_type_dict[line.account_id.account_type] == 'Por pagar':
                    move_line_hard_rent = line
                    break

            self.hard_rent = move_line_hard_rent.credit if move_line_hard_rent else 0.00
            self.neto_rent = self.hard_rent - self.deduccion_cost
            self.inv_retention_igv = 0.00
            self.retention_rate = 0.00
            self.tax_withheld = 0.00

        else:
            self.inv_retention_igv = 0.00
            self.hard_rent = 0.00
            self.neto_rent = 0.00
            self.retention_rate = 0.00
            self.tax_withheld = 0.00


class LinkEconomic(models.Model):
    _name = 'link.economic'
    _description = 'Vínculo Contribuyente - Residente en el extranjero'

    code = fields.Char('Codigo', required=True, size=2)
    name = fields.Char('Nombre', required=True)
    description = fields.Text('Descripcion')
    law = fields.Char('Ley')

    @api.constrains('code')
    def _constrains_codigo(self):
        for rec in self:
            if len(str(rec.code)) != 2:
                raise Warning('El campo código debe contener 2 dígitos.')


class TypeRent(models.Model):
    _name = 'type.rent'
    _description = 'Tipo de Renta'

    code = fields.Char('Codigo', size=2, required=True)
    name = fields.Text('Nombre', required=True)
    description = fields.Text('Descipcion')
    law = fields.Char('Ley', size=100)
    ocde = fields.Char('OCDE', size=8)


class ServiceTaken(models.Model):
    _name = 'service.taken'
    _description = 'Servicio Prestado'
    _rec_name = 'desctiption'

    code = fields.Char('Código', required=True, size=1)
    desctiption = fields.Char('Descripcion', size=100)
