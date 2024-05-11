from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    person_signature = fields.Binary(string='Signature', help="Field for adding the signature of the sales person")
    note = fields.Char(string="Note")


    @api.constrains('person_signature')
    def _check_person_signature(self):
        for order in self:
            if not order.person_signature:
                raise ValidationError("Please sign the document to proceed.")
