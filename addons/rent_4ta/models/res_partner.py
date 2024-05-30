from odoo import api, fields, models



class ResPartner(models.Model):
    _inherit = 'res.partner'
        
    double_taxation = fields.Selection(
        string='Convenio para evitar la doble tributación',
        selection=[
            ('0', '[0] Ninguno'),
            ('1', '[1] Canada'),
            ('2', '[2] Chile'),
            ('3', '[3] Can'),
            ('4', '[4] Brasil'),
        ],
        groups='hr.group_hr_user'
    )