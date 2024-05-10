from odoo import api, fields, models, _
import pytz
from odoo.exceptions import RedirectWarning, UserError, ValidationError
class Account(models.Model):
    _inherit = 'account.account'

    ple_date_account = fields.Date(
        string='Fecha de cuenta',
        default=fields.Date.today
    )
    ple_state_account = fields.Selection(
        selection=[
        ('1', '1'),
        ('8', '8'),
        ('9', '9')], 
        string='Estado', 
        default='1'
    )
    ple_selection = fields.Selection(
        selection=[],
        string='PLE'
    )


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    ple_journal_correlative = fields.Selection(
        selection=[
            ('A', 'Apertura'),
            ('C', 'Cierre'),
            ('M', 'Movimiento')],
        default='M',
        string='Estado PLE'
    )
    ple_no_include = fields.Boolean(
        string='No includir en Registro del PLE',
        default=False,
        help="Si este campo está marcado, las facturas (documentos de compra y venta), que tengan este diario seteado, no aparecerán en el registro de compras o ventas del PLE."
             " Sin perjuicio de que los asientos contables que dichas facturas generen, aparecerán en los libros que se elaboren con base a los asientos contables, como son el Libro Diario y Mayor."
        )


class AccountMove(models.Model):
    _inherit = 'account.move'

    ple_state = fields.Selection(
        selection=[
            ('0', '0'),
            ('1', '1'),
            ('2', '2'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8'),
            ('9', '9')],
        string='Estado PLE'
    )
    ple_its_declared = fields.Boolean(
        string='Declarado?'
    )
    ple_date = fields.Date(
        string='Fecha PLE',
        help='Esta fecha sirve para decidir en qué periodo del PLE se presentará esta factura en el registro de compras'
    )

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('form'):
            tags = [('group', 'ple_group')]
            arch, view = self.env['res.partner']._tags_invisible_per_country(arch, view, tags, [self.env.ref('base.pe')])
        return arch, view

    def update_ple_state(self):
        recs = self.filtered(lambda x: x.move_type in ['out_invoice', 'out_refund'])
        recs.update({'ple_state': '1'})

    @api.onchange('date')
    def onchange_ple_date_from_date(self):
        self.ple_date = self.date

    @api.onchange('invoice_date')
    def onchange_ple_date_from_invoice_date(self):
        self.ple_date = self.invoice_date

    @api.model
    def _convert_date_timezone(self, date_order, format_time='%Y-%m-%d %H:%M:%S'):
        user_tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        date_tz = pytz.utc.localize(date_order).astimezone(user_tz)
        date_order = date_tz.strftime(format_time)
        return date_order

    @api.model_create_multi
    def create(self, values):
        for vals in values:
            if vals.get('date'):
                vals['ple_date'] = vals['date']
            elif vals.get('invoice_date'):
                vals['ple_date'] = vals['invoice_date']
            else:
                vals['ple_date'] = fields.Date.context_today(self)
        obj = super(AccountMove, self).create(values)
        obj.update_ple_state()
        obj.update_lines_correlative()
        return obj

    def write(self, values):
        for rec in self:
            rec.update_cancel_ple_state(values)
            prefix = rec.get_ple_type_contributor()
            i = 1
            for line in rec.line_ids:
                line.update_correlative_cr(prefix, i)
                i += 1
            rec.change_ple_state_version(values)
        return super(AccountMove, self).write(values)

    def update_lines_correlative(self):
        for obj in self:
            prefix = obj.get_ple_type_contributor()
            obj.line_ids.update_correlative(prefix)

    def update_cancel_ple_state(self, values):
        self.ensure_one()
        document_type_id = self.l10n_latam_document_type_id and self.l10n_latam_document_type_id.code in ['01', '03']
        if self.move_type in ['out_invoice', 'out_refund'] and document_type_id and values.get('state') and values['state'] == 'cancel':
            values['ple_state'] = '2'
        return values

    def get_ple_type_contributor(self):
        self.ensure_one()
        new_name = self.journal_id.ple_journal_correlative or ''
        return new_name

    def change_ple_state_version(self, values):
        if self.move_type in ['out_invoice', 'out_refund']:
            if 'ple_date' in values:
                ple_month = values['ple_date'].split('-')
                for recs in self:
                    if recs.invoice_date and recs.date:
                        if recs.invoice_date.month < int(ple_month[1]) or recs.invoice_date.year < int(ple_month[0]):
                            values['ple_state'] = '8'
                        else:
                            values['ple_state'] = '1'
        self.update_cancel_ple_state(values)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ple_correlative = fields.Char(
        string='Correlativo'
    )

    def update_correlative(self, move_prefix):
        i = 1
        for line in self:
            if line.ple_correlative and line.ple_correlative != move_prefix:
                line.ple_correlative = '{}{}'.format(move_prefix, str(i).zfill(9))
            i += 1

    def update_correlative_cr(self, move_prefix, i):
        for line in self:
            if not line.ple_correlative:
                ple_correlative = '{}{}'.format(move_prefix, str(i).zfill(9))
                self._cr.execute("""UPDATE account_move_line
                                    SET ple_correlative=%s
                                    WHERE id=%s """,
                                 (ple_correlative, self.id))

class AccountReport(models.Model):
    _inherit = 'account.report'

    def _get_lines(self, options, all_column_groups_expression_totals=None):
        self.ensure_one()

        if options['report_id'] != self.id:
            # Should never happen; just there to prevent BIG issues and directly spot them
            raise UserError(
                _("Inconsistent report_id in options dictionary. Options says %s; report is %s.", options['report_id'],
                  self.id))

        # Necessary to ensure consistency of the data if some of them haven't been written in database yet
        self.env.flush_all()

        # Merge static and dynamic lines in a common list
        if all_column_groups_expression_totals is None:
            all_column_groups_expression_totals = self._compute_expression_totals_for_each_column_group(
                self.line_ids.expression_ids, options)

        dynamic_lines = self._get_dynamic_lines(options, all_column_groups_expression_totals)

        lines = []
        line_cache = {}  # {report_line: report line dict}
        hide_if_zero_lines = self.env['account.report.line']

        # There are two types of lines:
        # - static lines: the ones generated from self.line_ids
        # - dynamic lines: the ones generated from a call to the functions referred to by self.dynamic_lines_generator
        # This loops combines both types of lines together within the lines list
        for line in self.line_ids:  # _order ensures the sequence of the lines
            # Inject all the dynamic lines whose sequence is inferior to the next static line to add
            while dynamic_lines and line.sequence > dynamic_lines[0][0]:
                lines.append(dynamic_lines.pop(0)[1])

            parent_generic_id = line_cache[line.parent_id][
                'id'] if line.parent_id and line.parent_id in line_cache else None  # The parent line has necessarily been treated in a previous iteration
            line_dict = self._get_static_line_dict(options, line, all_column_groups_expression_totals,
                                                   parent_id=parent_generic_id)
            line_cache[line] = line_dict

            if line.hide_if_zero:
                hide_if_zero_lines += line

            lines.append(line_dict)

        for dummy, left_dynamic_line in dynamic_lines:
            lines.append(left_dynamic_line)

        # Manage growth comparison
        if self._display_growth_comparison(options):
            for line in lines:
                first_value, second_value = line['columns'][0]['no_format'], line['columns'][1]['no_format']

                if not first_value and not second_value:  # For layout lines and such, with no values
                    line['growth_comparison_data'] = {'name': '', 'class': ''}
                else:
                    green_on_positive = True
                    model, line_id = self._get_model_info_from_id(line['id'])

                    if model == 'account.report.line' and line_id:
                        report_line = self.env['account.report.line'].browse(line_id)
                        compared_expression = report_line.expression_ids.filtered(
                            lambda expr: expr.label == line['columns'][0]['expression_label']
                        )
                        green_on_positive = compared_expression.green_on_positive

                    line['growth_comparison_data'] = self._compute_growth_comparison_column(
                        options, first_value, second_value, green_on_positive=green_on_positive
                    )

        # Manage hide_if_zero lines:
        # - If they have column values: hide them if all those values are 0 (or empty)
        # - If they don't: hide them if all their children's column values are 0 (or empty)
        # Also, hide all the children of a hidden line.
        hidden_lines_dict_ids = set()
        for line in hide_if_zero_lines:
            children_to_check = line
            current = line
            while current:
                children_to_check |= current
                current = current.children_ids

            all_children_zero = True
            hide_candidates = set()
            for child in children_to_check:
                child_line_dict_id = line_cache[child]['id']

                if child_line_dict_id in hidden_lines_dict_ids:
                    continue
                elif all(col.get('is_zero', True) for col in line_cache[child]['columns']):
                    hide_candidates.add(child_line_dict_id)
                else:
                    all_children_zero = False
                    break

            if all_children_zero:
                hidden_lines_dict_ids |= hide_candidates

        lines[:] = filter(
            lambda x: x['id'] not in hidden_lines_dict_ids and x.get('parent_id') not in hidden_lines_dict_ids, lines)

        # Create the hierarchy of lines if necessary
        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)

        # Handle totals below sections for static lines
        lines = self._add_totals_below_sections(lines, options)

        # Unfold lines (static or dynamic) if necessary and add totals below section to dynamic lines
        lines = self._fully_unfold_lines_if_needed(lines, options)

        if self.custom_handler_model_id:
            lines = self.env[self.custom_handler_model_name]._custom_line_postprocessor(self, options, lines)

        return lines
