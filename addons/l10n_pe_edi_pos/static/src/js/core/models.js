odoo.define("l10n_pe_edi_pos.models", function (require) {
    "use strict";
    var rpc = require("web.rpc");
    const {PosGlobalState, Order} = require("point_of_sale.models");
    const Registries = require("point_of_sale.Registries");
    const EdiPosGlobalState = (PosGlobalState) =>
        class EdiPosGlobalState extends PosGlobalState {
            constructor(obj) {
                super(obj);
                this.journals = {};
                this.journals_by_id = {};
                this.suppliers = {};
            }
            async _processData(loadedData) {
                super._processData(loadedData);
                this.l10n_latam_identification =
                    loadedData["l10n_latam.identification.type"];
                this.db.save_l10n_latam_identification(this.l10n_latam_identification);
                this.l10n_latam_document = loadedData["l10n_latam.document.type"];
                this.db.save_l10n_latam_document(this.l10n_latam_document);
                this.journals = loadedData["account.journal"];
                this.get_journals_by_id(this.journals);
                this.suppliers = loadedData["l10n_pe_edi.supplier"];
            }
            get_journals_by_id(journals) {
                for (var i = 0; i < journals.length; i++) {
                    this.journals_by_id[journals[i].id] = journals[i];
                }
            }
            get_suppliers() {
                const suppliers = this.suppliers;
                this.company.l10n_pe_edi_ose = null;
                for (var i = 0; i < suppliers.length; i++) {
                    if (suppliers[i].id === this.company.l10n_pe_edi_ose_id[0]) {
                        this.company.l10n_pe_edi_ose = suppliers[i];
                    }
                }
            }
        };
    Registries.Model.extend(PosGlobalState, EdiPosGlobalState);
    const JPosOrder = (Order) =>
        class JPosOrder extends Order {
            init_from_JSON(json) {
                const result = super.init_from_JSON(...arguments);
                if (json.payment_journal_id) {
                    this.invoice_journal_id = json.payment_journal_id;
                    this.journals_by_id = json.payment_journal_id;
                }
                if (this.account_move) {
                    this.invoice = this.get_invoice();
                    this.invoice.then((invoice) => (this.invoice = invoice));
                }
                if (json.account_move_name) {
                    this.account_move_name = json.account_move_name;
                }
                return result;
            }
            export_as_JSON() {
                const json = super.export_as_JSON(...arguments);
                if (this.payment_journal_id) {
                    json.invoice_journal_id = this.payment_journal_id;
                    json.journals_by_id = this.payment_journal_id;
                }
                if (this.account_move) {
                    json.invoice = this.get_invoice();
                    json.invoice.then((invoice) => (this.invoice = invoice));
                }
                if (this.account_move_name) {
                    json.account_move_name = this.account_move_name;
                }
                return json;
            }
            export_for_printing() {
                var receipt = super.export_for_printing(...arguments);
                if (this.pos.get_order().invoice) {
                    receipt.invoice = this.pos.get_order().invoice;
                }
                if (this.invoice) {
                    receipt.invoice = this.invoice;
                }
                return receipt;
            }
            set_invoice(invoice) {
                this.invoice = invoice;
            }

            get_invoice() {
                self = this;
                return rpc
                    .query({
                        model: "pos.order",
                        method: "get_move",
                        args: [self.backendId],
                    })
                    .then(function (invoice) {
                        return invoice;
                    });
            }
        };
    Registries.Model.extend(Order, JPosOrder);
});
