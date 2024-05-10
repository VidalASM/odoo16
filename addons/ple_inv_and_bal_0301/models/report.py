from odoo import api, models


class GetLines(models.AbstractModel):
    _name = 'report.ple_inv_and_bal_0301.print_status_finance'
    _template = 'ple_inv_and_bal_0301.print_status_finance'

    @api.model
    def _get_report_values(self, docids=None, data=None):
        lines_ids = self.env['ple.report.inv.bal'].browse(docids)
        return {
            'doc_ids': docids,
            'docs': lines_ids,
            'data': data,
        }
