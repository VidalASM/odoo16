from math import copysign

from odoo import fields, models, _


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    READONLY_STATES = {
        'model': [('readonly', True)],
        'open': [('readonly', True)],
        'paused': [('readonly', True)],
        'close': [('readonly', True)],
        'cancelled': [('readonly', True)]
    }

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        required=True,
        related=False,
        store=True,
        state=READONLY_STATES,
        default=lambda self: self.env.company.currency_id.id
    )

    def compute_depreciation_board(self):
        self.ensure_one()
        new_depreciation_moves_data = self._recompute_board()

        # Need to unlink draft move before adding new one because if we create new move before, it will cause an error
        # in the compute for the depreciable/cumulative value
        self.depreciation_move_ids.filtered(lambda mv: mv.state == 'draft').unlink()
        new_depreciation_moves = self.env['account.move'].create(new_depreciation_moves_data)
        for new_depreciation_move in new_depreciation_moves:
            new_depreciation_move.with_context(check_move_validity=False)._onchange_currency_move_type_entry()

        if self.state == 'open':
            # In case of the asset is in running mode, we post in the past and set to auto post move in the future
            new_depreciation_moves._post()

        return True

    def _recompute_board(self):
        depreciation_moves = super()._recompute_board()

        if self.currency_id != self.company_id.currency_id:
            to_force_exchange_rate = self._get_to_force_exchange_rate()
            for move in depreciation_moves:
                move['to_force_exchange_rate'] = to_force_exchange_rate

        return depreciation_moves

    def _get_to_force_exchange_rate(self):
        return self.env['res.currency']._get_conversion_rate(
            from_currency=self.company_id.currency_id,
            to_currency=self.currency_id,
            company=self.company_id,
            date=self.acquisition_date or fields.Date.context_today(self),
        )
        
    def _get_disposal_moves(self, invoice_lines_list, disposal_date):
        """Create the move for the disposal of an asset.

        :param invoice_lines_list: list of recordset of `account.move.line`
            Each element of the list corresponds to one record of `self`
            These lines are used to generate the disposal move
        :param disposal_date: the date of the disposal
        """
        def get_line(asset, amount, account):
            if asset.currency_id != self.company_id.currency_id:
                return (0, 0, {
                    'name': asset.name,
                    'account_id': account.id,
                    # 'balance': -amount,
                    'analytic_distribution': analytic_distribution,
                    'currency_id': asset.currency_id.id,
                    'amount_currency': -amount
                })

            return (0, 0, {
                'name': asset.name,
                'account_id': account.id,
                'balance': -amount,
                'analytic_distribution': analytic_distribution,
                'currency_id': asset.currency_id.id,
                'amount_currency': -asset.company_id.currency_id._convert(
                    from_amount=amount,
                    to_currency=asset.currency_id,
                    company=asset.company_id,
                    date=disposal_date,
                )
            })

        move_ids = []
        assert len(self) == len(invoice_lines_list)
        for asset, invoice_line_ids in zip(self, invoice_lines_list):
            asset._create_move_before_date(disposal_date)

            analytic_distribution = asset.analytic_distribution

            dict_invoice = {}
            invoice_amount = 0

            initial_amount = asset.original_value
            initial_account = asset.original_move_line_ids.account_id if len(asset.original_move_line_ids.account_id) == 1 else asset.account_asset_id

            all_lines_before_disposal = asset.depreciation_move_ids.filtered(lambda x: x.date <= disposal_date)
            depreciated_amount = asset.currency_id.round(copysign(
                sum(all_lines_before_disposal.mapped('depreciation_value')) + asset.already_depreciated_amount_import,
                -initial_amount,
            ))
            depreciation_account = asset.account_depreciation_id
            for invoice_line in invoice_line_ids:
                dict_invoice[invoice_line.account_id] = copysign(invoice_line.balance, -initial_amount) + dict_invoice.get(invoice_line.account_id, 0)
                invoice_amount += copysign(invoice_line.balance, -initial_amount)
            list_accounts = [(amount, account) for account, amount in dict_invoice.items()]
            difference = -initial_amount - depreciated_amount - invoice_amount
            difference_account = asset.company_id.gain_account_id if difference > 0 else asset.company_id.loss_account_id
            line_datas = [(initial_amount, initial_account), (depreciated_amount, depreciation_account)] + list_accounts + [(difference, difference_account)]
            vals = {
                'asset_id': asset.id,
                'ref': asset.name + ': ' + (_('Disposal') if not invoice_line_ids else _('Sale')),
                'asset_depreciation_beginning_date': disposal_date,
                'date': disposal_date,
                # the currency attribute is modified in the message, so that the currency of the asset is shown and not that of the company
                'currency_id': asset.currency_id.id,
                'journal_id': asset.journal_id.id,
                'move_type': 'entry',
                'line_ids': [get_line(asset, amount, account) for amount, account in line_datas if account],
            }
            asset.write({'depreciation_move_ids': [(0, 0, vals)]})
            move_ids += self.env['account.move'].search([('asset_id', '=', asset.id), ('state', '=', 'draft')]).ids

        return move_ids
