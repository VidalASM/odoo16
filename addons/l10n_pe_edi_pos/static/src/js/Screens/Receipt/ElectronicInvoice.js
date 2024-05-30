odoo.define("l10n_pe_edi_pos.ElectronicInvoice", function (require) {
    "use strict";
    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");

    const PosInvPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            setup() {
                super.setup();
            }

            async _finalizeValidation() {
                var self = this;
                // self.currentOrder.set_to_invoice(false);
                console.log(self);
                if (
                    this.currentOrder.is_paid_with_cash() &&
                    this.env.pos.config.iface_cashdrawer
                ) {
                    this.env.pos.proxy.printer.open_cashbox();
                }
                var domain = [["pos_reference", "=", this.currentOrder.name]];
                var fields = this.currentOrder.name;

                this.currentOrder.initialize_validation_date();
                this.currentOrder.finalized = true;

                let syncOrderResult, hasError;

                try {
                    // 1. Save order to server.
                    syncOrderResult = await this.env.pos.push_single_order(
                        this.currentOrder
                    );

                    // 2. Invoice.
                    // if (this.currentOrder.is_to_invoice()) {
                    //     if (syncOrderResult.length) {
                    //         await this.env.legacyActionManager.do_action(
                    //             "account.account_invoices",
                    //             {
                    //                 additional_context: {
                    //                     active_ids: [syncOrderResult[0].account_move],
                    //                 },
                    //             }
                    //         );
                    //     } else {
                    //         throw {
                    //             code: 401,
                    //             message: "Backend Invoice",
                    //             data: {order: this.currentOrder},
                    //         };
                    //     }
                    // }

                    // 3. Post process.
                    if (
                        syncOrderResult.length &&
                        this.currentOrder.wait_for_push_order()
                    ) {
                        console.log("Validation order");
                        console.log(syncOrderResult);
                        const postPushResult = await this._postPushOrderResolve(
                            this.currentOrder,
                            syncOrderResult.map((res) => res.id)
                        );
                        if (!postPushResult) {
                            this.showPopup("ErrorPopup", {
                                title: this.env._t("Error: no internet connection."),
                                body: this.env._t(
                                    "Some, if not all, post-processing after syncing order failed."
                                ),
                            });
                        }
                    }
                } catch (error) {
                    if (error.code === 700 || error.code === 701) this.error = true;

                    if ("code" in error) {
                        // We started putting `code` in the rejected object for invoicing error.
                        // We can continue with that convention such that when the error has `code`,
                        // then it is an error when invoicing. Besides, _handlePushOrderError was
                        // introduce to handle invoicing error logic.
                        await this._handlePushOrderError(error);
                    } else {
                        // We don't block for connection error. But we rethrow for any other errors.
                        if (isConnectionError(error)) {
                            this.showPopup("OfflineErrorPopup", {
                                title: this.env._t("Connection Error"),
                                body: this.env._t(
                                    "Order is not synced. Check your internet connection"
                                ),
                            });
                        } else {
                            throw error;
                        }
                    }
                }
                if (
                    this.currentOrder.is_to_invoice() &&
                    this.env.pos.config.l10n_pe_edi_send_invoice
                ) {
                    this.rpc({
                        model: "pos.order",
                        method: "invoice_data",
                        args: [fields],
                    }).then(function (output) {
                        if (output !== false) {
                            self.currentOrder.invoice = output;
                            // Self.currentOrder.invoice_number = output.invoice_number;
                            // self.currentOrder.type_of_invoice_document =
                            //     output.type_of_invoice_document;
                            // self.currentOrder.igv_percent = output.igv_percent;
                            // self.currentOrder.amount_in_words = output.amount_in_words;
                            // self.currentOrder.currency_name = output.currency_name;
                            // self.currentOrder.authorization_message =
                            //     output.authorization_message;
                            // self.currentOrder.control_url = output.control_url;
                            // self.currentOrder.barcode = output.barcode;
                            // self.currentOrder.date_invoice = output.date_invoice;
                            // self.currentOrder.invoice_date_due =
                            //     output.invoice_date_due;
                            self.showScreen(self.nextScreen);
                        }
                    });
                } else {
                    this.showScreen(this.nextScreen);
                }
                // Remove the order from the local storage so that when we refresh the page, the order
                // won't be there
                this.env.pos.db.remove_unpaid_order(this.currentOrder);

                // Ask the user to sync the remaining unsynced orders.
                if (
                    !hasError &&
                    syncOrderResult &&
                    this.env.pos.db.get_orders().length
                ) {
                    const {confirmed} = await this.showPopup("ConfirmPopup", {
                        title: this.env._t("Remaining unsynced orders"),
                        body: this.env._t(
                            "There are unsynced orders. Do you want to sync these orders?"
                        ),
                    });
                    if (confirmed) {
                        // NOTE: Not yet sure if this should be awaited or not.
                        // If awaited, some operations like changing screen
                        // might not work.
                        this.env.pos.push_orders();
                    }
                }
            }
        };

    Registries.Component.extend(PaymentScreen, PosInvPaymentScreen);

    return PosInvPaymentScreen;
});
