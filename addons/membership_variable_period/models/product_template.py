# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
import math
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_next_date(self, date, qty=1):
        """Get the date that results on incrementing given date an interval of
        time in time unit.
        @param date: Original date.
        @param unit: Interval time unit.
        @param interval: Quantity of the time unit.
        @rtype: date
        @return: The date incremented in 'interval' units of 'unit'.
        """
        res = super()._get_next_date(date, qty=qty)
        if self.membership_type == "variable":
            delta = self.membership_interval_qty * int(math.ceil(qty))
            if isinstance(date, str):
                date = fields.Date.from_string(date)
            if self.membership_interval_unit == "days":
                return date + timedelta(days=delta)
            elif self.membership_interval_unit == "weeks":
                return date + timedelta(weeks=delta)
            elif self.membership_interval_unit == "months":
                return date + relativedelta(months=delta)
            elif self.membership_interval_unit == "years":
                return date + relativedelta(years=delta)
        return res  # pragma: no cover

    membership_type = fields.Selection(
        selection=[("fixed", "Fixed dates"), ("variable", "Variable periods")],
        default="fixed",
        required=True,
    )
    membership_interval_qty = fields.Integer(
        string="Interval quantity",
        default=1,
        # Technically only required if membership_type is variable, but because
        # there's a default value, this should be fine, and should prevent bad
        # scenarios where a value is expected but none is available.
        required=True,
    )
    membership_interval_unit = fields.Selection(
        string="Interval Unit",
        selection=[
            ("days", "days"),
            ("weeks", "weeks"),
            ("months", "months"),
            ("years", "years"),
        ],
        default="years",
        # Same comment as on membership_interval_qty in re being required.
        required=True,
    )

    def _correct_vals_membership_type(self, vals, membership_type):
        if membership_type == "variable":
            vals["membership_date_from"] = vals["membership_date_to"] = False
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        fixed_vals_list = []
        for vals in vals_list:
            fixed_vals = vals.copy()
            membership_type = fixed_vals.get("membership_type", "fixed")
            fixed_vals = self._correct_vals_membership_type(fixed_vals, membership_type)
            fixed_vals_list.append(fixed_vals)
        return super().create(fixed_vals_list)

    def write(self, vals):
        if not vals.get("membership_type"):
            return super().write(vals)
        for rec in self:
            vals2 = vals.copy()
            rec._correct_vals_membership_type(
                vals2, vals.get("membership_type", rec.membership_type)
            )
            super(ProductTemplate, rec).write(vals2)
        return True

    @api.constrains(
        "membership_date_from",
        "membership_date_to",
        "membership",
        "membership_type",
    )
    def _check_membership_dates(self):
        return super(
            ProductTemplate,
            self.filtered(lambda record: record.membership_type == "fixed"),
        )._check_membership_dates()
