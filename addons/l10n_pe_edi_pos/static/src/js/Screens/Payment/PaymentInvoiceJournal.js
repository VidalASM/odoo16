odoo.define("l10n_pe_edi_pos.PaymentInvoiceJournal", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require("point_of_sale.Registries");

    class PaymentInvoiceJournal extends PosComponent {
        setup() {
            super.setup();
        }
        get isSelected() {
            const selectedOrder = this.env.pos.get_order();
            if (
                this.props.paymentInvoiceJournal.id === selectedOrder.payment_journal_id
            ) {
                return true;
            }
            return false;
        }
    }

    PaymentInvoiceJournal.template = "PaymentInvoiceJournal";

    Registries.Component.add(PaymentInvoiceJournal);

    return PaymentInvoiceJournal;
});
