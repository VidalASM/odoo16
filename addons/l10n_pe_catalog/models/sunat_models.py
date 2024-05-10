from odoo import fields, models, api


class ModelSunatCatalog(models.AbstractModel):
    _name = 'model.sunat.catalog'
    _description = 'Modelo catálogo de SUNAT'

    name = fields.Char(
        string='Nombre',
        compute='compute_name'
    )
    code = fields.Char(
        string='Código',
        required=True
    )
    description = fields.Char(
        string='Descripción',
        required=True
    )

    @api.depends('code', 'description')
    def compute_name(self):
        for rec in self:
            rec.name = "[%s] %s" % (rec.code or '', rec.description or '')


class IgvAfectationType(models.Model):
    _name = 'igv.afectation.type'
    _description = '[07] Tipo de Afectación al IGV'
    _inherit = 'model.sunat.catalog'


class ChargeDiscountCodes(models.Model):
    _name = 'charge.discount.codes'
    _description = '[53] Códigos de cargos o descuentos'
    _inherit = 'model.sunat.catalog'


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    l10n_pe_charge_discount_id = fields.Many2one(
        comodel_name='charge.discount.codes',
        string='[53] Códigos de cargos o descuentos'
    )


class ClassificationServices(models.Model):
    _name = 'classification.services'
    _description = '[30] Clasificación de los bienes y servicios adquiridos'

    code = fields.Char(
        string='Código',
        required=True
    )

    description = fields.Char(
        string='Descripción',
        required=True
    )

    def name_get(self):
        res = []
        for partner in self:
            name = partner.description
            res.append((partner.id, name))
        return res

class PaymentMethodsCodes(models.Model):
    _name = 'payment.methods.codes'
    _description = '[59] Códigos de medios de pago'
    _rec_name = 'description'

    code = fields.Char(
        string='Código',
        required=True
    )

    description = fields.Char(
        string='Descripción',
        required=True
    )
