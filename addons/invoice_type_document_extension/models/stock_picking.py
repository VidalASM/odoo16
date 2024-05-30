from odoo import api, models, fields, _

   
class StockPicking(models.Model):
    _inherit = 'stock.picking'    
    
    transfer_document_type_id = fields.Many2one(
        comodel_name='l10n_latam.document.type',
        string='Tipo doc. traslado',
        help='Esta serie se utiliza para el PLE 13.1, si lo deja en Blanco, Odoo lo completará con valores por defecto que provienen de '
             'la guía de Remisión, sino, de la Orden de compra o de venta, sino, lo completará con 00.',
    )
    serie_transfer_document = fields.Char(
        string='Serie doc. traslado',
        help='Esta serie se utiliza para el PLE 13.1, si lo deja en Blanco, Odoo lo completará con valores por defecto que provienen de '
             'la guía de Remisión, sino, de la Orden de compra o de venta, sino, lo completará con 00.',
        compute='_compute_transfer_data_picking',
        inverse='_set_transfer_data_picking',
        store=True,
    )
    number_transfer_document = fields.Char(
        string='Número doc. traslado',
        help='Esta serie se utiliza para el PLE 13.1, si lo deja en Blanco, Odoo lo completará con valores por defecto que provienen de '
             'la guía de Remisión, sino, de la Orden de compra o de venta, sino, lo completará con 00.',
        compute='_compute_transfer_data_picking',
        inverse='_set_transfer_data_picking',
        store=True,
    )
    
    def _set_transfer_data_picking(self):
        pass

    @api.depends('purchase_id.invoice_ids.ref', 'sale_id.invoice_ids.name', 'picking_number')
    def _compute_transfer_data_picking(self):
        for picking in self:
            if (picking.picking_number and not picking.number_transfer_document and not picking.serie_transfer_document and not picking.transfer_document_type_id) and (
                picking.picking_number and '-' in picking.picking_number):
                data = picking.picking_number.split('-')
                picking.serie_transfer_document = data[0]
                picking.number_transfer_document = data[1]
                picking.transfer_document_type_id = False
            else:
                serie_transfer_document = None
                number_transfer_document = None
                transfer_document_type_id = None
                invoice = []
                flag = 1
                if picking.purchase_id:
                    invoice = picking.purchase_id.invoice_ids
                elif picking.sale_id:
                    flag = 2
                    invoice = picking.sale_id.invoice_ids

                for rec in invoice:
                    if (rec.ref and '-' in rec.ref) and flag == 1:
                        data = rec.ref.split('-')
                        serie_transfer_document = data[0]
                        number_transfer_document = data[1]
                        transfer_document_type_id = rec.l10n_latam_document_type_id
                    if rec.name and '-' in rec.name and flag == 2:
                        data = rec.name.split('-')
                        serie_transfer_document = data[0]
                        number_transfer_document = data[1]
                        transfer_document_type_id = rec.l10n_latam_document_type_id
                picking.serie_transfer_document = serie_transfer_document
                picking.number_transfer_document = number_transfer_document
                picking.transfer_document_type_id = transfer_document_type_id

    def massive_serie_number_type(self):
        for i in self:
            if i.serie_transfer_document == '' or not i.serie_transfer_document or i.number_transfer_document == '' or not i.number_transfer_document or i.transfer_document_type_id == '' or not i.transfer_document_type_id:
                i._compute_transfer_data_picking()
            else:
                pass

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('form'):
            tags = [
                ('field', 'transfer_document_type_id'),
                ('field', 'serie_transfer_document'),
                ('field', 'number_transfer_document')
            ]
            arch, view = self.env['res.partner']._tags_invisible_per_country(arch, view, tags, [self.env.ref('base.pe')])
        return arch, view
