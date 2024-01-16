odoo.define("l10n_pe_edi_pos.OdooFactReceipt", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const OrderReceipt = require("point_of_sale.OrderReceipt");

    const L10nPeEdiPosReceipt = (OrderReceipt) =>
        class extends OrderReceipt {
            setup() {
                super.setup();
                this._receiptEnv = this.props.order.getOrderReceiptEnv();
            }
        };

    Registries.Component.extend(OrderReceipt, L10nPeEdiPosReceipt);
    if (
        self.odoo.session_info &&
        self.odoo.session_info.config.l10n_pe_edi_send_invoice
    ) {
        OrderReceipt.template = "L10nPeEdiPosReceipt";
    }
    Registries.Component.add(L10nPeEdiPosReceipt);
    return OrderReceipt;
});
