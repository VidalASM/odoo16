from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends('purchase_id.invoice_ids.ref', 'sale_id.invoice_ids.name', 'pos_order_id.account_move.name')
    def _compute_transfer_data(self):
        for picking in self:
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
            elif picking.pos_order_id:
                flag = 3
                invoice = picking.pos_order_id.account_move

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
                if rec.name and '-' in rec.name and flag == 3:
                    data = rec.name.split('-')
                    serie_transfer_document = data[0]
                    number_transfer_document = data[1]
                    transfer_document_type_id = rec.l10n_latam_document_type_id
            picking.serie_transfer_document = serie_transfer_document
            picking.number_transfer_document = number_transfer_document
            picking.transfer_document_type_id = transfer_document_type_id

    def massive_serie_number_type(self):
        res = super(StockPicking, self).massive_serie_number_type()
        for rec in self:
            type_rec = rec.transfer_document_type_id
            serie_rec = rec.serie_transfer_document
            number_rec = rec.number_transfer_document
            if not type_rec or type_rec is None or not serie_rec or serie_rec is None or not number_rec or number_rec is None:
                rec._compute_transfer_data()
            else:
                pass
        return res
