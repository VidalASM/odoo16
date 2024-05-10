import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models
from odoo.tools import float_is_zero, float_compare

DAYS_PER_MONTH = 30
DAYS_PER_YEAR = DAYS_PER_MONTH * 12

ple_asset_book = [
    ('assets_book_acquisition_asset', '7.1 Registro de Activos Fijos - Adquisiciones - Activo'),
    ('assets_book_acquisition_amortization', '7.1 Registro de Activos Fijos - Adquisiciones - Amortización'),
    ('assets_book_improvements_asset', '7.1 Registro de Activos Fijos - Mejoras - Activo'),
    ('assets_book_other_asset', '7.1 Registro de Activos Fijos - Otros Ajustes - Activo'),
    ('assets_book_other_amortization', '7.1 Registro de Activos Fijos - Otros Ajustes - Amortización'),
    ('assets_book_voluntary_revaluation_asset', '7.1 Registro de Activos Fijos - Reval. Voluntaria - Activo'),
    ('assets_book_voluntary_revaluation_amortization', '7.1 Registro de Activos Fijos - Reval. Voluntaria - Amortización'),
    ('assets_book_revaluation_reorganization_asset', '7.1 Registro de Activos Fijos - Reval. Reorg. - Activo'),
    ('assets_book_revaluation_reorganization_amortization', '7.1 Registro de Activos Fijos - Reval. Reorg. - Amortzación'),
    ('assets_book_revaluation_other_asset', '7.1 Registro de Activos Fijos - Reval. Otras - Activo'),
    ('assets_book_revaluation_other_amortization', '7.1 Registro de Activos Fijos - Reval. Otras - Amortización'),
    ('assets_book_inflation_asset', '7.1 Registro de Activos Fijos - Inflación - Activo'),
    ('assets_book_inflation_amortization', '7.1 Registro de Activos Fijos - Inflación - Amortización')
]


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    asset_catalog_code = fields.Selection(
        selection=[
            ('1', "[1] Naciones Unidas"),
            ('3', "[3] GS1 (EAN-UCC)"),
            ('9', "[9] Otros")],
        string="Catálogo de existencias",
        default='9'
    )
    asset_code = fields.Char(
        string="Código de existencias"
    )
    asset_cubso_osce = fields.Char(
        string="Código CUBSO u OSCE"
    )
    fixed_asset_type = fields.Selection(
        selection=[
            ('1', "[1] Sin efecto tributario"),
            ('2', "[2] Revaluado con Efecto Tributario")],
        string="Tipo de Activo Fijo",
        default='1'
    )
    fixed_asset_state = fields.Selection(
        selection=[
            ('1', "[1] Activos en Desuso"),
            ('2', "[2] Activos Obsoletos"),
            ('9', "[9] Resto de Activos")],
        string="Estado del Activo Fijo",
        default='1'
    )
    depreciation_method = fields.Selection(
        selection=[
            ('1', "[1] Línea Recta"),
            ('2', "[2] Unidades producidas"),
            ('9', "[9] Otros")],
        string="Método de depreciación",
        default='1'
    )
    authorization_number_method_change = fields.Char(string="N° Autorización cambio de método", )
    asset_rate = fields.Float(
        string='Tasa',
        digits=(16, 2)
    )

    first_depreciation_date_import = fields.Date(help="In case of an import from another software, provide the first depreciation date in it.")

    def _compute_board_amount(self, residual_amount, period_start_date, period_end_date, days_already_depreciated, days_left_to_depreciated, residual_declining):

        days_until_period_end = self._get_delta_days(self.paused_prorata_date, period_end_date)
        days_before_period = self._get_delta_days(self.paused_prorata_date, period_start_date + relativedelta(days=-1))
        days_before_period = max(days_before_period, 0)  # if disposed before the beginning of the asset for example
        number_days = days_until_period_end - days_before_period
        if self.asset_lifetime_days == 0:
            return 0, 0

        if self.method in ('degressive', 'degressive_then_linear'):
            # Declining by year but divided per month
            # We compute the amount of the period based on ratio how many days there are in the period
            # e.g: monthly period = 30 days --> (30/360) * 12000 * 0.4
            # => For each month in the year we will decline the same amount.
            amount = (number_days / DAYS_PER_YEAR) * residual_declining * self.method_progress_factor
        else:
            computed_linear_amount = self._get_linear_amount(days_before_period, days_until_period_end, self.book_value)
            if float_compare(residual_amount, 0, precision_rounding=self.currency_id.rounding) >= 0:
                linear_amount = min(computed_linear_amount, residual_amount)
                amount = max(linear_amount, 0)
            else:
                linear_amount = max(computed_linear_amount, residual_amount)
                amount = min(linear_amount, 0)

        if self.method == 'degressive_then_linear':
            if not self.parent_id:
                linear_amount = self._get_linear_amount(days_before_period, days_until_period_end, self.total_depreciable_value)
            else:
                # we want to know the amount before the reeval for the parent so the child can follow the same curve,
                # so it transitions from degressive to linear at the same moment
                parent_moves = self.parent_id.depreciation_move_ids.filtered(lambda mv: mv.date <= self.prorata_date).sorted(key=lambda mv: (mv.date, mv.id))
                parent_cumulative_depreciation = parent_moves[-1].asset_depreciated_value if parent_moves else self.parent_id.already_depreciated_amount_import
                parent_depreciable_value = parent_moves[-1].asset_remaining_value if parent_moves else self.parent_id.total_depreciable_value
                if self.currency_id.is_zero(parent_depreciable_value):
                    linear_amount = self._get_linear_amount(days_before_period, days_until_period_end, self.total_depreciable_value)
                else:
                    # To have the same curve as the parent, we need to have the equivalent amount before the reeval.
                    # The child's depreciable value corresponds to the amount that is left to depreciate for the parent.
                    # So, we use the proportion between them to compute the equivalent child's total to depreciate.
                    # We use it then with the duration of the parent to compute the depreciation amount
                    depreciable_value = self.total_depreciable_value * (1 + parent_cumulative_depreciation/parent_depreciable_value)
                    linear_amount = self._get_linear_amount(days_before_period, days_until_period_end, depreciable_value) * self.asset_lifetime_days / self.parent_id.asset_lifetime_days
            amount = max(linear_amount, amount, key=abs)

        # if self.method == 'degressif_chelou' and days_left_to_depreciated != 0:
        #     linear_amount = number_days * residual_declining / days_left_to_depreciated
        #     if float_compare(residual_amount, 0, precision_rounding=self.currency_id.rounding) >= 0:
        #         amount = max(linear_amount, amount)
        #     else:
        #         amount = min(linear_amount, amount)

        # This part was commented to avoid paid the depreciated amount
        #if abs(residual_amount) < abs(amount) or days_until_period_end >= self.asset_lifetime_days:
            # If the residual amount is less than the computed amount, we keep the residual amount
            # If total_days is greater or equals to asset lifetime days, it should mean that
            # the asset will finish in this period and the value for this period is equal to the residual amount.
            amount = residual_amount
        return number_days, self.currency_id.round(amount)
    
    def _recompute_board(self, start_depreciation_date=False):
        self.ensure_one()
        # All depreciation moves that are posted
        posted_depreciation_move_ids = self.depreciation_move_ids.filtered(
            lambda mv: mv.state == 'posted' and not mv.asset_value_change
        ).sorted(key=lambda mv: (mv.date, mv.id))

        imported_amount = self.already_depreciated_amount_import
        residual_amount = self.value_residual
        if not posted_depreciation_move_ids:
            residual_amount += imported_amount
        residual_declining = residual_amount

        start_depreciation_date = start_depreciation_date or self.paused_prorata_date
        if not self.parent_id:
            final_depreciation_date = self.paused_prorata_date + relativedelta(months=int(self.method_period) * self.method_number, days=-1)
        else:
            # If it has a parent, we want the increase only for the remaining days the parent has
            final_depreciation_date = self.parent_id.paused_prorata_date + relativedelta(months=int(self.parent_id.method_period) * self.parent_id.method_number, days=-1)

        final_depreciation_date = self._get_end_period_date(final_depreciation_date)
        depreciation_move_values = []
        if not float_is_zero(self.value_residual, precision_rounding=self.currency_id.rounding):
            while not self.currency_id.is_zero(residual_amount) and start_depreciation_date < final_depreciation_date:
                period_end_depreciation_date = self._get_end_period_date(start_depreciation_date)
                period_end_fiscalyear_date = self.company_id.compute_fiscalyear_dates(period_end_depreciation_date).get('date_to')

                days, amount = self._compute_board_amount(residual_amount, start_depreciation_date, period_end_depreciation_date, False, False, residual_declining)
                residual_amount -= amount

                # This part was commented to avoid months skipped calculated as part of the depreciated amount
                '''
                if not posted_depreciation_move_ids:
                    # self.already_depreciated_amount_import management.
                    # Subtracts the imported amount from the first depreciation moves until we reach it
                    # (might skip several depreciation entries)
                    if abs(imported_amount) <= abs(amount):
                        amount -= imported_amount
                        imported_amount = 0
                    else:
                        imported_amount -= amount
                        amount = 0
                '''

                if self.method == 'degressive_then_linear' and final_depreciation_date < period_end_depreciation_date:
                    period_end_depreciation_date = final_depreciation_date

                if not float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    # For deferred revenues, we should invert the amounts.
                    if self.asset_type == 'sale':
                        amount *= -1
                    depreciation_move_values.append(self.env['account.move']._prepare_move_for_asset_depreciation({
                        'amount': amount,
                        'asset_id': self,
                        'depreciation_beginning_date': start_depreciation_date,
                        'date': period_end_depreciation_date,
                        'asset_number_days': days,
                    }))

                if period_end_depreciation_date == period_end_fiscalyear_date:
                    residual_declining = residual_amount

                start_depreciation_date = period_end_depreciation_date + relativedelta(days=1)

        return depreciation_move_values

class AccountAccount(models.Model):
    _inherit = 'account.account'

    ple_selection = fields.Selection(selection_add=ple_asset_book)

class AccountMove(models.Model):
    _inherit = 'account.move'

    asset_remaining_value = fields.Monetary(string='Depreciable Value', compute='_compute_depreciation_cumulative_value', store=True)
