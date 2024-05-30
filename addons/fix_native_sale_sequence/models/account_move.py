from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    _sequence_yearly_regex = r'^(?P<prefix1>.*?)(?P<year>((?<=\\D)|(?<=^))((20|21)?\\d{2}))(?P<prefix2>\\D+?)(?P<seq>\\d*)(?P<suffix>\\D*?)$'
