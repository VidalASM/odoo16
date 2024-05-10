from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, formatLang


class AccountMove(models.Model):
    _inherit = 'account.move'
        
    def _log_depreciation_asset(self):
        for move in self.filtered(lambda m: m.asset_id):
            asset = move.asset_id
            # the currency attribute is modified in the message, so that the currency of the asset is shown and not that of the company
            msg = _('Entrada de depreciación %s contabilizada (%s)') % (move.name, formatLang(self.env, move.depreciation_value, currency_obj=move.asset_id.currency_id))
            asset.message_post(body=msg)

    def _auto_create_asset(self):
        create_list = []
        invoice_list = []
        auto_validate = []
        for move in self:
            if not move.is_invoice():
                continue

            for move_line in move.line_ids.filtered(lambda line: not (move.move_type in ('out_invoice', 'out_refund') and line.account_id.internal_group == 'asset')):
                if (
                    move_line.account_id
                    and (move_line.account_id.can_create_asset)
                    and move_line.account_id.create_asset != "no"
                    and not move.reversed_entry_id
                    and not (move_line.currency_id or move.currency_id).is_zero(move_line.price_total)
                    and not move_line.asset_ids
                    and not move_line.tax_line_id
                    and move_line.price_total > 0
                ):
                    if not move_line.name:
                        raise UserError(_('Journal Items of {account} should have a label in order to generate an asset').format(account=move_line.account_id.display_name))
                    if move_line.account_id.multiple_assets_per_line:
                        units_quantity = max(1, int(move_line.quantity))
                    else:
                        units_quantity = 1
                    vals = {
                        'name': move_line.name,
                        'company_id': move_line.company_id.id,
                        'currency_id': move_line.currency_id.id,
                        'analytic_distribution': move_line.analytic_distribution,
                        'original_value': move_line.price_unit,
                        'original_move_line_ids': [(6, False, move_line.ids)],
                        'state': 'draft',
                    }
                    model_id = move_line.account_id.asset_model
                    if model_id:
                        vals.update({
                            'model_id': model_id.id,
                        })
                    auto_validate.extend([move_line.account_id.create_asset == 'validate'] * units_quantity)
                    invoice_list.extend([move] * units_quantity)
                    for i in range(1, units_quantity + 1):
                        if units_quantity > 1:
                            vals['name'] = move_line.name + _(" (%s of %s)", i, units_quantity)
                        create_list.extend([vals.copy()])

        assets = self.env['account.asset'].create(create_list)
        for asset, vals, invoice, validate in zip(assets, create_list, invoice_list, auto_validate):
            if 'model_id' in vals:
                asset._onchange_model_id()
                if validate:
                    asset.validate()
            if invoice:
                asset_name = {
                    'purchase': _('Asset'),
                    'sale': _('Deferred revenue'),
                    'expense': _('Deferred expense'),
                }[asset.asset_type]
                msg = _('%s created from invoice') % (asset_name)
                msg += ': <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>' % (invoice.id, invoice.name)
                asset.message_post(body=msg)
        return assets

    def _get_depreciation(self):
        asset = self.asset_id
        if asset:
            account = asset.account_depreciation_expense_id if asset.asset_type == 'sale' else asset.account_depreciation_id
            field = 'debit' if asset.asset_type == 'sale' or \
                               any(move.move_type == 'in_refund' for move in asset.original_move_line_ids.move_id) else 'credit'
            asset_depreciation = sum(
                self.line_ids.filtered(lambda l: l.account_id == account).mapped(field)
            )
            # Special case of closing entry
            if any(
                    (line.account_id, line[field]) == (asset.account_asset_id, asset.original_value)
                    for line in self.line_ids
            ):
                rfield = 'debit' if asset.asset_type != 'sale' else 'credit'
                asset_depreciation = (
                        asset.original_value
                        - asset.salvage_value
                        - sum(
                    self.line_ids.filtered(lambda l: l.account_id == account).mapped(rfield)
                )
                )
        else:
            asset_depreciation = 0
        if self.currency_id == asset.currency_id and self.currency_id.name == 'USD' and asset.currency_id != self.company_currency_id:
            asset_depreciation = round(asset_depreciation / self.exchange_rate, 2)
        return asset_depreciation

    @api.model
    def _prepare_move_for_asset_depreciation(self, vals):
        missing_fields = set(['asset_id', 'amount', 'depreciation_beginning_date', 'date', 'asset_number_days']) - set(vals)
        if missing_fields:
            raise UserError(_('Some fields are missing {}').format(', '.join(missing_fields)))
        asset = vals['asset_id']
        analytic_distribution = asset.analytic_distribution
        depreciation_date = vals.get('date', fields.Date.context_today(self))
        company_currency = asset.company_id.currency_id
        current_currency = asset.currency_id
        prec = company_currency.decimal_places
        amount_currency = vals['amount']
        # amount = current_currency._convert(amount_currency, company_currency, asset.company_id, depreciation_date)
        amount = amount_currency
        # Keep the partner on the original invoice if there is only one
        partner = asset.original_move_line_ids.mapped('partner_id')
        partner = partner[:1] if len(partner) <= 1 else self.env['res.partner']
        move_line_1 = {
            'name': asset.name,
            'partner_id': partner.id,
            'account_id': asset.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'analytic_distribution': analytic_distribution,
            'currency_id': current_currency.id,
            'amount_currency': -amount_currency,
        }
        move_line_2 = {
            'name': asset.name,
            'partner_id': partner.id,
            'account_id': asset.account_depreciation_expense_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'analytic_distribution': analytic_distribution,
            'currency_id': current_currency.id,
            'amount_currency': amount_currency,
        }
        move_vals = {
            'partner_id': partner.id,
            'date': depreciation_date,
            'journal_id': asset.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            'asset_id': asset.id,
            'ref': _("%s: Depreciation", asset.name),
            'asset_depreciation_beginning_date': vals['depreciation_beginning_date'],
            'asset_number_days': vals['asset_number_days'],
            'name': '/',
            'asset_value_change': vals.get('asset_value_change', False),
            'move_type': 'entry',
            'currency_id': current_currency.id,
        }
        return move_vals

    @api.depends('line_ids.balance')
    def _compute_depreciation_value(self):
        super()._compute_depreciation_value()
        for move in self:
            asset = move.asset_id or move.reversed_entry_id.asset_id  # reversed moves are created before being assigned to the asset
            if asset and asset.currency_id != asset.company_id.currency_id:
                account_internal_group = 'income' if asset.asset_type == 'sale' else 'expense'
                asset_depreciation = sum(
                    move.line_ids.filtered(lambda l: l.account_id.internal_group == account_internal_group or l.account_id == asset.account_depreciation_expense_id).mapped('amount_currency')
                ) * (-1 if asset.asset_type == 'sale' else 1)
                move.depreciation_value = asset_depreciation
