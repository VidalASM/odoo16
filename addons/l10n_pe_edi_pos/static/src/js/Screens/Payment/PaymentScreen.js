odoo.define("l10n_pe_edi_pos.PaymentScreen", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const {useListener} = require("@web/core/utils/hooks");
    const PaymentScreen = require("point_of_sale.PaymentScreen");

    const L10nPEPosPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            setup() {
                super.setup();
                this.env.pos.company.l10n_pe_edi_ose = null;
                useListener("click-journal", this.setJournal);
                console.log(this.env.pos);
                if (this.env.pos.config.auto_check_invoice) {
                    this.currentOrder.set_to_invoice(true);
                }
            }
            async setJournal(event) {
                const selectedOrder = this.currentOrder;
                selectedOrder.payment_journal_id = event.detail.id;
                // SelectedOrder.trigger('change', selectedOrder);
            }
            async _postPushOrderResolve(order, order_server_ids) {
                try {
                    if (
                        order.is_to_invoice() &&
                        this.env.pos.config.l10n_pe_edi_send_invoice
                    ) {
                        const result = await this.rpc({
                            model: "pos.order",
                            method: "get_move",
                            args: [order_server_ids],
                        }).then(function (invoice) {
                            return invoice;
                        });
                        order.set_invoice(result || null);
                    }
                } finally {
                    return super._postPushOrderResolve(...arguments);
                }
            }
            async validateOrder(isForceValidate) {
                // this.currentOrder.set_to_invoice(false);
                // this.to_invoice = false;
                // console.log(this.currentOrder);
                // Validación personalizada del campo del pedido
                // if (this.env.pos.config.l10n_pe_edi_send_invoice) {
                //     this.showPopup('ErrorPopup', {
                //         title: 'Error',
                //         body: 'Custom field is required.',
                //     });
                //     return;
                // }
                if (this.currentOrder && this.env.pos.config.l10n_pe_edi_send_invoice) {
                    const client = this.currentOrder.get_partner();
                    const order = this.currentOrder;
                    let type_document;
                    _.each(order.pos.journals, function (doc) {
                        // console.log("Documento id");
                        // console.log(doc);
                        if (order.payment_journal_id == doc.id) {
                            type_document = doc.l10n_latam_document_type_id[0];
                        }
                    });
                    if (!type_document) {
                        this.showPopup("ErrorPopup", {
                            title: this.env._t("ALERT"),
                            body: this.env._t("Please select a Document type."),
                        });
                        return false;
                    }
                    
                    if (type_document === 13){
                        console.log("tipo de documento");
                        console.log(type_document);
                        this.currentOrder.assert_editable();
                        this.currentOrder.to_invoice = false;
                    }

                    var type_document_model =
                        this.env.pos.db.l10n_latam_document_by_id[type_document];
                    if (client) {
                        var type_identification =
                            client.l10n_latam_identification_type_id[0];
                        if (!type_identification) {
                            this.showPopup("ErrorPopup", {
                                title: this.env._t("ALERT"),
                                body: this.env._t(
                                    "Select the Identification type of the client: " +
                                        client.name
                                ),
                            });
                            return false;
                        }
                        var type_identification_model =
                            this.env.pos.db.l10n_latam_identification_by_id[
                                type_identification
                            ];
                        if (type_document_model.code === "03") {
                            if (type_identification_model.l10n_pe_vat_code === "1") {
                                if (client.vat.length !== 8) {
                                    const errorMessage =
                                        this.env._t("The DNI of the client: ") +
                                        client.name +
                                        this.env._t(", is not valid.");

                                    this.showPopup("ErrorPopup", {
                                        title: this.env._t("ALERT"),
                                        body: errorMessage,
                                    });
                                    return false;
                                }
                            }
                            if (type_identification_model.l10n_pe_vat_code === "6") {
                                if (client.vat.length !== 11) {
                                    this.showPopup("ErrorPopup", {
                                        title: this.env._t("ALERT"),
                                        body:
                                            this.env._t("The RUC  of the client: ") +
                                            client.name +
                                            this.env._t(", is not valid."),
                                    });
                                    return false;
                                }
                            }
                        }
                        if (type_document_model.code === "01") {
                            if (type_identification_model.l10n_pe_vat_code !== "6") {
                                this.showPopup("ErrorPopup", {
                                    title: this.env._t("ALERT"),
                                    body: this.env._t(
                                        "The document type 'Invoice' is valid only for clients with valid RUC."
                                    ),
                                });
                                return false;
                            }
                            if (client.vat.length !== 11) {
                                this.showPopup("ErrorPopup", {
                                    title: this.env._t("ALERT"),
                                    body:
                                        this.env._t("The RUC of the client: ") +
                                        client.name +
                                        this.env._t(", is not valid."),
                                });
                                return false;
                            }
                        }
                    }
                }

                // Llamada al método padre para la validación de orden estándar
                // super.validateOrder(options);
                // this.currentOrder.finalized = false;
                // this.currentOrder.finalized = true;
                // this.currentOrder.set_to_invoice(false);
                return await super.validateOrder(...arguments);
            }
        };
    Registries.Component.extend(PaymentScreen, L10nPEPosPaymentScreen);

    return PaymentScreen;
});
