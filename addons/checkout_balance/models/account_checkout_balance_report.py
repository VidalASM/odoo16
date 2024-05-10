from odoo import models, fields, _
from odoo.tools import float_compare
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class CheckoutBalanceCustomHandler(models.AbstractModel):
    _name = 'account.checkout.balance.report.handler'
    _description = 'Checkout Balance Custom Handler'
    _inherit = 'account.report.custom.handler'

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals):
        def _update_column(line, column_key, new_value, blank_if_zero=True):
            line['columns'][column_key]['name'] = self.env['account.report'].format_value(new_value, figure_type='monetary', blank_if_zero=blank_if_zero)
            line['columns'][column_key]['no_format'] = new_value

        def _update_balance_columns(line, debit_column_key, credit_column_key, total_diff_values_key, account_group_type):
            def _get_column_value(column_key):
                if column_key is not None:
                    return line['columns'][column_key]['no_format']
                return False

            def _update_total_diff_values(debit_value, credit_value):
                if debit_value and credit_value:
                    new_debit_value = 0.0
                    new_credit_value = 0.0
                    if float_compare(debit_value, credit_value, precision_digits=self.env.company.currency_id.decimal_places) == 1:
                        new_debit_value = debit_value - credit_value
                        total_diff_values[total_diff_values_key]['debit'] += new_debit_value
                    else:
                        new_credit_value = (debit_value - credit_value) * -1
                        total_diff_values[total_diff_values_key]['credit'] += new_credit_value
                    _update_column(line, debit_column_key, new_debit_value)
                    _update_column(line, credit_column_key, new_credit_value)
                else:
                    if debit_value:
                        total_diff_values[total_diff_values_key]['debit'] += debit_value
                    if credit_value:
                        total_diff_values[total_diff_values_key]['credit'] += credit_value

            debit_value = _get_column_value(debit_column_key)
            credit_value = _get_column_value(credit_column_key)

            if total_diff_values_key in ('initial_balance', 'end_balance'):
                if debit_value and credit_value:
                    new_debit_value = 0.0
                    new_credit_value = 0.0
                    
                    if float_compare(debit_value, credit_value, precision_digits=self.env.company.currency_id.decimal_places) == 1:
                        new_debit_value = debit_value - credit_value
                        total_diff_values[total_diff_values_key] += credit_value
                    else:
                        new_credit_value = (debit_value - credit_value) * -1
                        total_diff_values[total_diff_values_key] += debit_value

                    _update_column(line, debit_column_key, new_debit_value)
                    _update_column(line, credit_column_key, new_credit_value)
            elif total_diff_values_key == 'general_balance':
                if account_group_type == 'balance':
                    _update_total_diff_values(debit_value, credit_value)
                else:
                    _update_column(line, debit_column_key, 0.0)
                    _update_column(line, credit_column_key, 0.0)
            elif total_diff_values_key == 'eerr_function_balance':
                if account_group_type in ('function', 'both'):
                    _update_total_diff_values(debit_value, credit_value)
                else:
                    _update_column(line, debit_column_key, 0.0)
                    _update_column(line, credit_column_key, 0.0)
            elif total_diff_values_key == 'eerr_nature_balance':
                if account_group_type in ('nature', 'both'):
                    _update_total_diff_values(debit_value, credit_value)
                else:
                    _update_column(line, debit_column_key, 0.0)
                    _update_column(line, credit_column_key, 0.0)

        def _find_indices_by_label(options, label):
            indices = {'debit': None, 'credit': None}
            for debit_credit in ['debit', 'credit']:
                index = next((index for index, column in enumerate(options['columns']) if column.get('expression_label') == debit_credit and column.get('column_label') == label), None)
                indices[debit_credit] = index
            return indices
        
        def _insert_balance_values(balance_key, debit_index, credit_index):
            difference = total_diff_values[balance_key]['debit'] - total_diff_values[balance_key]['credit']
            if difference > 0:
                # Result of the Exercise or Period
                result_exercise_period_columns.insert(debit_index, {
                    'name': report.format_value(0.0, figure_type='monetary', blank_if_zero=True),
                    'no_format': 0.0,
                    'class': 'number'
                })
                result_exercise_period_columns.insert(credit_index, {
                    'name': report.format_value(difference, figure_type='monetary', blank_if_zero=True),
                    'no_format': difference,
                    'class': 'number'
                })
                # Totals
                totals_debit = total_diff_values[balance_key]['debit']
                totals_credit = total_diff_values[balance_key]['credit'] + difference
            elif difference < 0:
                # Result of the Exercise or Period
                result_exercise_period_columns.insert(debit_index, {
                    'name': report.format_value(-difference, figure_type='monetary', blank_if_zero=True),
                    'no_format': -difference,
                    'class': 'number'
                })
                result_exercise_period_columns.insert(credit_index, {
                    'name': report.format_value(0.0, figure_type='monetary', blank_if_zero=True),
                    'no_format': 0.0,
                    'class': 'number'
                })
                # Totals
                totals_debit = total_diff_values[balance_key]['debit'] - difference
                totals_credit = total_diff_values[balance_key]['credit']
            else:
                # Result of the Exercise or Period
                for _ in range(2):
                    result_exercise_period_columns.append({
                        'name': report.format_value(0.0, figure_type='monetary', blank_if_zero=True),
                        'no_format': 0.0,
                        'class': 'number'
                    })
                # Totals
                totals_debit = total_diff_values[balance_key]['debit']
                totals_credit = total_diff_values[balance_key]['credit']
                
            result_totals_columns.insert(debit_index, {
                'name': report.format_value(totals_debit, figure_type='monetary', blank_if_zero=False),
                'no_format': totals_debit,
                'class': 'number'
            })
            result_totals_columns.insert(credit_index, {
                'name': report.format_value(totals_credit, figure_type='monetary', blank_if_zero=False),
                'no_format': totals_credit,
                'class': 'number'
            }) 

        lines = [line[1] for line in self.env['account.general.ledger.report.handler']._dynamic_lines_generator(report, options, all_column_groups_expression_totals)]

        total_diff_values = {
            'initial_balance': 0.0,
            'end_balance': 0.0,
            'general_balance': {'debit': 0.0, 'credit': 0.0},
            'eerr_function_balance': {'debit': 0.0, 'credit': 0.0},
            'eerr_nature_balance': {'debit': 0.0, 'credit': 0.0},
        }
        
        # Initial balance
        init_balance_indices = _find_indices_by_label(options, 'initial_column')
        init_balance_debit_index = init_balance_indices['debit']
        init_balance_credit_index = init_balance_indices['credit']
        
        # End balance
        end_balance_indices = _find_indices_by_label(options, 'end_column')
        end_balance_debit_index = end_balance_indices['debit']
        end_balance_credit_index = end_balance_indices['credit']
        
        # General balance
        general_balance_indices = _find_indices_by_label(options, 'general_column')
        general_balance_debit_index = general_balance_indices['debit']
        general_balance_credit_index = general_balance_indices['credit']
        
        # EERR by Function
        eerr_function_balance_indices = _find_indices_by_label(options, 'eerr_function_column')
        eerr_function_balance_debit_index = eerr_function_balance_indices['debit']
        eerr_function_balance_credit_index = eerr_function_balance_indices['credit']
        
        # EERR by Nature
        eerr_nature_balance_indices = _find_indices_by_label(options, 'eerr_nature_column')
        eerr_nature_balance_debit_index = eerr_nature_balance_indices['debit']
        eerr_nature_balance_credit_index = eerr_nature_balance_indices['credit']

        for line in lines[:-1]:
            model, record_id = report._get_model_info_from_id(line['id'])
            if model == 'account.account':
                account = self.env[model].browse(record_id)
                account_group_type = account.group_id.type_group if account and account.group_id else ''
                
                # Initial balance
                _update_balance_columns(line, init_balance_debit_index, init_balance_credit_index, 'initial_balance', account_group_type)
                
                # End balance
                _update_balance_columns(line, end_balance_debit_index, end_balance_credit_index, 'end_balance', account_group_type)
    
                # General balance
                _update_balance_columns(line, general_balance_debit_index, general_balance_credit_index, 'general_balance', account_group_type)
                
                # EERR by Function
                _update_balance_columns(line, eerr_function_balance_debit_index, eerr_function_balance_credit_index, 'eerr_function_balance', account_group_type)
                
                # EERR by Nature
                _update_balance_columns(line, eerr_nature_balance_debit_index, eerr_nature_balance_credit_index, 'eerr_nature_balance', account_group_type)

            line.pop('expand_function', None)
            line.pop('groupby', None)
            line.update({
                'unfoldable': False,
                'unfolded': False,
                'class': 'o_account_searchable_line o_account_coa_column_contrast',
            })

            res_model = report._get_model_info_from_id(line['id'])[0]
            if res_model == 'account.account':
                line['caret_options'] = 'checkout_balance_account_account'
        
        # Total Lines
        if lines:
            total_line = lines[-1]
            
            # Total Initial Balance and End Balance
            for index, balance_key in zip((
                init_balance_debit_index, init_balance_credit_index, 
                end_balance_debit_index, end_balance_credit_index), (
                    'initial_balance', 'initial_balance', 
                    'end_balance', 'end_balance'
                )
            ):
                if index is not None:
                    _update_column(total_line, index, total_line['columns'][index]['no_format'] - total_diff_values[balance_key], blank_if_zero=False)

            # Total General Balance, EERR Function Balance y EERR Nature Balance
            for index, balance_key in zip((
                general_balance_debit_index, general_balance_credit_index,
                eerr_function_balance_debit_index, eerr_function_balance_credit_index,
                eerr_nature_balance_debit_index, eerr_nature_balance_credit_index), (
                    'general_balance', 'general_balance',
                    'eerr_function_balance', 'eerr_function_balance',
                    'eerr_nature_balance', 'eerr_nature_balance'
                )
            ):
                if index is not None:
                    # If the index is a multiple of 2 then it is debit
                    if index % 2 == 0:
                        _update_column(total_line, index, total_diff_values[balance_key]['debit'], blank_if_zero=False) 
                    else:
                        _update_column(total_line, index, total_diff_values[balance_key]['credit'], blank_if_zero=False)

            # Result of the Exercise or Period
            result_exercise_period_line = {
                'id': report._get_generic_line_id(None, None, markup='total'),
                'name': _('Result of the Exercise or Period'),
                'class': 'total',
                'level': 1,
                'unfoldable': False,
                'unfolded': False,
                'caret_options': None,
                'action_id': None,
            }

            result_exercise_period_columns = [{
                    'name': report.format_value(0.0, figure_type='monetary', blank_if_zero=True),
                    'no_format': 0.0,
                    'class': 'number'
                } for _ in range(end_balance_credit_index + 1)
            ]
            
            # Totals
            result_totals_line = {
                'id': report._get_generic_line_id(None, None, markup='total'),
                'name': _('Totals'),
                'class': 'total',
                'level': 1,
                'unfoldable': False,
                'unfolded': False,
                'caret_options': None,
                'action_id': None,
            }
            
            result_totals_columns = [{
                    'name': report.format_value(0.0, figure_type='monetary', blank_if_zero=True),
                    'no_format': 0.0,
                    'class': 'number'
                } for _ in range(end_balance_credit_index + 1)
            ]

            balance_key_indices = {
                'general_balance': (general_balance_debit_index, general_balance_credit_index),
                'eerr_function_balance': (eerr_function_balance_debit_index, eerr_function_balance_credit_index),
                'eerr_nature_balance': (eerr_nature_balance_debit_index, eerr_nature_balance_credit_index),
            }

            for balance_key, (debit_index, credit_index) in balance_key_indices.items():
                if debit_index is not None and credit_index is not None:
                    _insert_balance_values(balance_key, debit_index, credit_index)

            result_exercise_period_line.update({'columns': result_exercise_period_columns})
            lines.append(result_exercise_period_line)
            
            result_totals_line.update({'columns': result_totals_columns})
            lines.append(result_totals_line)
            
        return [(0, line) for line in lines]

    def _caret_options_initializer(self):
        return {
            'checkout_balance_account_group': [
                {'name': _("Open Account Group"), 'action': 'open_account_group'},
            ],
            'checkout_balance_account_account': [
                {'name': _("General Ledger"), 'action': 'caret_option_open_general_ledger'},
                {'name': _("Journal Items"), 'action': 'open_journal_items'},
            ],
        }

    def _custom_options_initializer(self, report, options, previous_options=None):
        """ Modifies the provided options to add a column group for initial balance and end balance, as well as the appropriate columns.
        """
        super()._custom_options_initializer(report, options, previous_options=previous_options)
        default_group_vals = {'horizontal_groupby_element': {}, 'forced_options': {}}

        # Columns between initial and end balance must not include initial balance; we use a special option key for that in general ledger
        for column_group in options['column_groups'].values():
            column_group['forced_options']['general_ledger_strict_range'] = True

        if options['comparison']['periods']:
            # Reverse the order the group of columns with the same column_group_key while keeping the original order inside the group
            new_columns_order = []
            current_column = []
            current_column_group_key = options['columns'][-1]['column_group_key']

            for column in reversed(options['columns']):
                if current_column_group_key != column['column_group_key']:
                    current_column_group_key = column['column_group_key']
                    new_columns_order += current_column
                    current_column = []

                current_column.insert(0, column)
            new_columns_order += current_column

            options['columns'] = new_columns_order
            options['column_headers'][0][:] = reversed(options['column_headers'][0])

        # Initial balance
        initial_balance_options = self.env['account.general.ledger.report.handler']._get_options_initial_balance(options)
        initial_forced_options = {
            'date': initial_balance_options['date'], 
            'include_current_year_in_unaff_earnings': True
        }
        initial_header_element = [{'name': _("Initial Balance"), 'forced_options': initial_forced_options}]
        col_headers_initial = [
            initial_header_element,
            *options['column_headers'][1:],
        ]
        initial_column_group_vals = report._generate_columns_group_vals_recursively(col_headers_initial, default_group_vals)
        initial_columns, initial_column_groups = report._build_columns_from_column_group_vals(initial_forced_options, initial_column_group_vals)
        
        if initial_columns:
            for column in initial_columns:
                column['column_label'] = 'initial_column'

        end_date_to = options['date']['date_to']
        end_date_from = options['comparison']['periods'][-1]['date_from'] if options['comparison']['periods'] else options['date']['date_from']
        end_forced_options = {
            'date': {
                'mode': 'range',
                'date_to': fields.Date.from_string(end_date_to).strftime(DEFAULT_SERVER_DATE_FORMAT),
                'date_from': fields.Date.from_string(end_date_from).strftime(DEFAULT_SERVER_DATE_FORMAT)
            }
        }
        
        # End balance
        end_header_element = [{'name': _("End Balance"), 'forced_options': end_forced_options}]
        col_headers_end = [
            end_header_element,
            *options['column_headers'][1:],
        ]
        end_column_group_vals = report._generate_columns_group_vals_recursively(col_headers_end, default_group_vals)
        end_columns, end_column_groups = report._build_columns_from_column_group_vals(end_forced_options, end_column_group_vals)

        if end_columns:
            for column in end_columns:
                column['column_label'] = 'end_column'
        
        # General Balance
        general_header_element = [{'name': _("General Balance"), 'forced_options': end_forced_options}]
        col_headers_general = [
            general_header_element,
            *options['column_headers'][1:],
        ]
        general_column_group_vals = report._generate_columns_group_vals_recursively(col_headers_general, default_group_vals)
        general_columns, general_column_groups = report._build_columns_from_column_group_vals(end_forced_options, general_column_group_vals)

        if general_columns:
            for column in general_columns:
                column['column_label'] = 'general_column'

        # EERR by Function
        eerr_function_header_element = [{'name': _("EERR by Function"), 'forced_options': end_forced_options}]
        col_headers_eerr_function = [
            eerr_function_header_element,
            *options['column_headers'][1:],
        ]
        eerr_function_column_group_vals = report._generate_columns_group_vals_recursively(col_headers_eerr_function, default_group_vals)
        eerr_function_columns, eerr_function_column_groups = report._build_columns_from_column_group_vals(end_forced_options, eerr_function_column_group_vals)

        if eerr_function_columns:
            for column in eerr_function_columns:
                column['column_label'] = 'eerr_function_column'

        # EERR by Nature
        eerr_nature_header_element = [{'name': _("EERR by Nature"), 'forced_options': end_forced_options}]
        col_headers_eerr_nature = [
            eerr_nature_header_element,
            *options['column_headers'][1:],
        ]
        eerr_nature_column_group_vals = report._generate_columns_group_vals_recursively(col_headers_eerr_nature, default_group_vals)
        eerr_nature_columns, eerr_nature_column_groups = report._build_columns_from_column_group_vals(end_forced_options, eerr_nature_column_group_vals)

        if eerr_nature_columns:
            for column in eerr_nature_columns:
                column['column_label'] = 'eerr_nature_column'
        
        # Update options
        options['column_headers'][0] = initial_header_element + options['column_headers'][0] + end_header_element + general_header_element + eerr_function_header_element + eerr_nature_header_element
        options['column_groups'].update(initial_column_groups)
        options['column_groups'].update(end_column_groups)
        options['column_groups'].update(general_column_groups)
        options['column_groups'].update(eerr_function_column_groups)
        options['column_groups'].update(eerr_nature_column_groups)
        options['columns'] = initial_columns + options['columns'] + end_columns + general_columns + eerr_function_columns + eerr_nature_columns
        # So that GL does not compute them
        options['ignore_totals_below_sections'] = True
        
        report._init_options_order_column(options, previous_options)
        
    def _custom_line_postprocessor(self, report, options, lines):
        # Level 3 lines are not included
        lines = [line for line in lines if line.get('level', False) != 3]

        for line in lines:
            model, dummy = report._get_model_info_from_id(line['id'])
            
            if model == 'account.group':
                if options.get('hierarchy'):
                    line_classes = line.get('class', '')
                    line['class'] = line_classes + ' o_account_coa_column_contrast'

                if line['level'] == 2:
                    line['unfoldable'] = False
                    line['unfolded'] = False
                    line['caret_options'] = 'checkout_balance_account_group'
                
        return lines

    def _get_report_name(self):
        return _("Checkout x Account")

    def open_account_group(self, options, params=None):
        model, record_id = self.env['account.report']._get_model_info_from_id(params['line_id'])
        record = self.env[model].browse(record_id)
        return {
            'name': record.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.group',
            'view_mode': 'form',
            'view_id': False,
            'views': [(False, 'form')],
            'res_id': record.id,
        }
