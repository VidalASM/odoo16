odoo.define("l10n_pe_edi_pos.ClientDefault", function (require) {
    "use strict";
    const {PosGlobalState, Order} = require("point_of_sale.models");
    const Registries = require("point_of_sale.Registries");
    var core = require("web.core");
    var _t = core._t;

    const PosOrderDefaultCustomer = (PosGlobalState) =>
        class extends PosGlobalState {
            // @override
            createReactiveOrder(json) {
                const reactiveOrder = super.createReactiveOrder(...arguments);
                if (reactiveOrder.partner === null && this.config.default_partner_id) {
                    const partner = this.db.get_partner_by_id(
                        this.config.default_partner_id[0]
                    );
                    if (partner) {
                        reactiveOrder.set_partner(partner);
                    } else {
                        this.showPopup("ErrorPopup", {
                            title: this.env._t("Warning !!!"),
                            body:
                                this.config.default_partner_id[1] +
                                this.env._t(
                                    " set to Default Customer of new Order, but it Arichived it. Please Unarchive"
                                ),
                        });
                    }
                }
                return reactiveOrder;
            }
        };

    Registries.Model.extend(PosGlobalState, PosOrderDefaultCustomer);
});
