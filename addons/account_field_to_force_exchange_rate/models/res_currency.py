from odoo import models


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def _force_convert(self, from_amount, to_currency, company, force_rate, round=True):
        """Returns the converted amount of ``from_amount``` from the currency
           ``self`` to the currency ``to_currency`` for the given ``date`` and
           company.
           :param company: The company from which we retrieve the convertion rate
           :param round: Round the result or not
        """
        self, to_currency = self or to_currency, to_currency or self
        assert self, "convert amount from unknown currency"
        assert to_currency, "convert amount to unknown currency"
        assert company, "convert amount from unknown company"
        # apply conversion rate
        if self == to_currency:
            to_amount = from_amount
        else:
            to_amount = from_amount * (1 / force_rate)
        # apply rounding
        return to_currency.round(to_amount) if round else to_amount
