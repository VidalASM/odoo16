from odoo import fields, models


class ExonerationNodomicilied(models.Model):
    _name = 'exoneration.nodomicilied'
    _description = 'Exoneración no Domiciliado'

    code = fields.Integer(
        string='Código',
        required=True
    )
    name = fields.Text(
        string='Nombre',
        required=True
    )
    description = fields.Text(
        string='Descripcion'
    )


class ResCountry(models.Model):
    _inherit = 'res.country'

    l10n_pe_sunat_code = fields.Char(
        string='Código (Tabla 35 SUNAT)',
        help='Este código se completará en el libro electrónico de No domiciliados cada vez que una factura, tenga un proveedor asociado con este país.'
    )
