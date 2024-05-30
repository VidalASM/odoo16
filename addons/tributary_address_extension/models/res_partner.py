from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ubigeo = fields.Char(
        string='Ubigeo',
        size=6,
        default='150101',
        help='Aquí se consigna el código de ubicación geográfica (Ubigeo) de 6 dígitos, de acuerdo Catálogo N° 13 de SUNAT.'
    )
    annexed_establishment = fields.Char(
        string='Establecimientos Anexos',
        default='0000',
        help='Código asignado por SUNAT para el establecimiento anexo declarado en el RUC.'
    )

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('form'):
            tags = ['ubigeo', 'annexed_establishment']
            arch, view = self._tags_invisible_per_country(arch, view, tags, [self.env.ref('base.pe')])
        return arch, view
