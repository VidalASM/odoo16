from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    weight = fields.Float(string="Peso neto", compute="_cal_weight")
    gross_weight = fields.Float(string="Peso bruto", compute="_compute_gross_weight")

    transport_agency = fields.Many2one(
        comodel_name="res.partner", string="Agencia de Transporte"
    )
    volume = fields.Float(string="Volumen", compute="_compute_volume")

    options = [
        ("01", "Venta"),
        ("02", "Compra"),
        ("03", "Consignación"),
        ("04", "Devolución"),
        ("05", "Venta sujeta a confirmación"),
        ("06", "Traslado entre misma empresa"),
        ("07", "Traslado de bienes para transformación"),
        ("08", "Rojo de bienes transformados"),
        ("09", "Importación"),
        ("10", "Exportación"),
        ("11", "Venta con entrega a terceros"),
        ("12", "Consumo Interno"),
        ("13", "Transferencia Gratuita"),
        ("14", "Comodato"),
        ("15", "Otros"),
    ]

    select_options = fields.Selection(options, string="Motivo de Traslado MOA")

    cod_client_sucur = fields.Char(string="Código Cliente/Sucursal", related="partner_id.cod_client_sucur")

    @api.depends("move_line_ids.product_id.weight")
    def _cal_weight(self):
        for picking in self:
            if picking.move_line_ids and len(picking.move_line_ids) == 1:
                move_line = picking.move_line_ids
                picking.weight = (move_line.qty_done if picking.state == "done" else move_line.reserved_uom_qty) * move_line.product_id.weight
            else:
                picking.weight = sum((move_line.qty_done if picking.state == "done" else move_line.reserved_uom_qty) * move_line.product_id.weight for move_line in picking.move_line_ids if move_line.state != "cancel")

    @api.depends("move_line_ids.product_id.gross_weight")
    def _compute_gross_weight(self):
        for picking in self:
            picking.gross_weight = sum((move_line.qty_done if self.state == "done" else move_line.reserved_uom_qty) * move_line.product_id.gross_weight for move_line in picking.move_line_ids if move_line.state != "cancel")

    @api.depends("move_line_ids.product_id.volume")
    def _compute_volume(self):
        for picking in self:
            picking.volume = sum((move_line.qty_done if self.state == "done" else move_line.reserved_uom_qty) * move_line.product_id.volume for move_line in picking.move_line_ids if move_line.state != "cancel")

    #quitar hora de campo fecha de emisión
    def mod_date_done(self):
        if self.date_done:
            temp_date = self.date_done
            return temp_date.strftime("%d/%m/%Y")
        return ""

    #función para concatenar los campos de la dirección de partida
    def concatenated_fields_starting_point(self):
        if self.company_id.partner_id.l10n_pe_district.name and self.company_id.partner_id.city and self.company_id.partner_id.state_id.name:
            return str(self.company_id.partner_id.l10n_pe_district.name) + "/" + str(self.company_id.partner_id.city) + "/" + str(self.company_id.partner_id.state_id.name)
        return ""

    #función para concatenar los campos de la dirección de llegada
    def concatenated_fields_arrival(self):
        partner_city = self.partner_id.city if self.partner_id.city else (self.partner_id.parent_id.city_id.name if self.partner_id.parent_id else self.partner_id.city_id.name)
        if self.partner_id.l10n_pe_district.name and partner_city and self.partner_id.state_id.name:
            return str(self.partner_id.l10n_pe_district.name) + "/" + str(partner_city) + "/" + str(self.partner_id.state_id.name)
        return ""

    #función para concatenar mediante '-' el número de documento de comprobante
    def get_payment_proof_doc_num(self):
        if self.serie_transfer_document and self.number_transfer_document:
            return self.serie_transfer_document + "-" + self.number_transfer_document
        return ""