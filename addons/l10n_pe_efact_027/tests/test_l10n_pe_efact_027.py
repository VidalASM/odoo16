# -*- coding: utf-8 -*
from odoo.tests import tagged
from odoo.addons.l10n_pe_edi.tests.common import TestPeEdiCommon, mocked_l10n_pe_edi_post_invoice_web_service
from unittest.mock import patch

from freezegun import freeze_time


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestPeEfact027(TestPeEdiCommon):

    def test_invoice_payment_term(self):
        self.product.l10n_pe_withhold_percentage = 10
        self.product.l10n_pe_withhold_code = '027'
        with freeze_time(self.frozen_today), \
                patch('odoo.addons.l10n_pe_edi.models.account_edi_format.AccountEdiFormat._l10n_pe_edi_post_invoice_web_service',
                      new=mocked_l10n_pe_edi_post_invoice_web_service):
            update_vals_dict = {"l10n_pe_edi_operation_type": "1004",
                                "invoice_payment_term_id": self.env.ref("account.account_payment_term_advance_60days").id}
            invoice = self._create_invoice(**update_vals_dict).with_context(edi_test_mode=True)
            invoice.action_post()
        print('---- TEST L10N_PE_EFACT_027 OK  ----')
