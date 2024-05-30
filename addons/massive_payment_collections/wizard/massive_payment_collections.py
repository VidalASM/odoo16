from lxml import etree

from odoo import models, fields, api


class MassivePaymentCollections(models.TransientModel):
    _name = 'massive.payment.collections'
    _description = 'Register Massive Payment'
    _inherit = 'account.payment.register'

    amount = fields.Monetary(string='Amount')
    to_force_exchange_rate = fields.Float(
        string='Force T.C.',
        digits=(12, 12),
        compute='_compute_to_force_exchange_rate',
        store=True,
        help='This labels is used for force exchange rate.'
    )
    line_ids = fields.Many2many(
        'account.move.line',
        'massive_payment_collections_move_line_rel',
        'wizard_id',
        'line_id',
        string="Journal items",
        readonly=True,
        copy=False
    )
    hide_payment_method_line = fields.Boolean(
        compute='_compute_payment_method_line_fields',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'"
    )

    # payment_difference_handling = fields.Selection([
    #     ('open', 'Keep open'),
    #     ('reconcile', 'Mark as fully paid')],
    #     default='open',
    #     string="Payment Difference Handling"
    # )
    # writeoff_account_id = fields.Many2one(
    #     comodel_name='account.account',
    #     string="Difference Account",
    #     copy=False,
    #     domain="[('deprecated', '=', False), ('company_id', '=', company_id)]"
    # )
    # writeoff_label = fields.Char(
    #     string='Journal Item Label',
    #     default='Write-Off',
    #     help='Change label of the counterpart that will hold the payment difference'
    # )

    @api.depends('can_edit_wizard', 'payment_method_line_id')
    def _compute_to_force_exchange_rate(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                batches = wizard._get_batches()
                if wizard.payment_method_line_id.name == 'Detracción':
                    for batch in batches:
                        for line in batch['lines']:
                            invoice_date = line.move_id.invoice_date
                            rate_id = self.env['res.currency.rate'].search([('name', '<=', invoice_date)], order='name DESC',
                                                                   limit=1)
                            wizard.to_force_exchange_rate = rate_id[0].company_rate if rate_id else 0
                            break
                else:
                    wizard.to_force_exchange_rate = batches[0]['lines'][0].move_id.to_force_exchange_rate
            else:
                wizard.to_force_exchange_rate = 0

    @api.depends('payment_type', 'journal_id')
    def _compute_payment_method_line_fields(self):
        for wizard in self:
            wizard.available_payment_method_line_ids = wizard.journal_id._get_available_payment_method_lines(
                wizard.payment_type)
            if wizard.payment_method_line_id.id not in wizard.available_payment_method_line_ids.ids:
                wizard.hide_payment_method_line = False
            else:
                wizard.hide_payment_method_line = len(wizard.available_payment_method_line_ids) == 1 \
                                                  and wizard.available_payment_method_line_ids.code == 'manual'

    @api.depends('payment_type', 'journal_id')
    def _compute_payment_method_line_id(self):
        for wizard in self:
            available_payment_method_lines = wizard.journal_id._get_available_payment_method_lines(wizard.payment_type)

            if available_payment_method_lines:
                wizard.payment_method_line_id = available_payment_method_lines[0]._origin
            else:
                wizard.payment_method_line_id = False

    @api.depends('payment_method_line_id')
    def _compute_show_require_partner_bank(self):
        """ Computes if the destination bank account must be displayed in the payment form view. By default, it
        won't be displayed but some modules might change that, depending on the payment type."""
        for wizard in self:
            wizard.show_partner_bank_account = wizard.payment_method_line_id.code in self.env[
                'account.payment']._get_method_codes_using_bank_account()
            wizard.require_partner_bank_account = wizard.payment_method_line_id.code in self.env[
                'account.payment']._get_method_codes_needing_bank_account()

    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id',
                 'payment_date')
    def _compute_amount(self):
        for wizard in self:
            if wizard.source_currency_id == wizard.currency_id:
                wizard.amount = wizard.source_amount_currency
            elif wizard.currency_id == wizard.company_id.currency_id:
                wizard.amount = wizard.source_amount
            else:
                amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount,
                                                                                 wizard.currency_id, wizard.company_id,
                                                                                 wizard.payment_date)
                wizard.amount = amount_payment_currency

    @api.depends('amount')
    def _compute_payment_difference(self):
        for wizard in self:
            if wizard.source_currency_id == wizard.currency_id:
                wizard.payment_difference = wizard.source_amount_currency - wizard.amount
            elif wizard.currency_id == wizard.company_id.currency_id:
                wizard.payment_difference = wizard.source_amount - wizard.amount
            else:
                amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount,
                                                                                 wizard.currency_id, wizard.company_id,
                                                                                 wizard.payment_date)
                wizard.payment_difference = amount_payment_currency - wizard.amount

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            form_view = self.env.ref('massive_payment_collections.view_massive_payment_collections_form')
            tree = etree.fromstring(res['arch'])
            if res.get('view_id') == form_view.id and len(
                    tree.xpath("//field[@name='available_partner_bank_ids']")) == 0:
                arch_tree = etree.fromstring(form_view.arch)
                if arch_tree.tag == 'form':
                    arch_tree.insert(0, etree.Element('field', attrib={
                        'name': 'available_partner_bank_ids',
                        'invisible': '1',
                    }))
                    form_view.sudo().write({'arch': etree.tostring(arch_tree, encoding='unicode')})
                    return super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                   submenu=submenu)
        return res
