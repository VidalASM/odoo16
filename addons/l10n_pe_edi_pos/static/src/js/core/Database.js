odoo.define("l10n_pe_edi_pos.Database", function (require) {
    var db = require("point_of_sale.DB");

    db.include({
        init: function (options) {
            this._super(options);
            this.l10n_latam_identification_by_id = {};
            this.l10n_latam_document_by_id = {};
        },
        save_l10n_latam_identification: function (l10n_latam_identification) {
            for (var i = 0; i < l10n_latam_identification.length; i++) {
                var latam = l10n_latam_identification[i];
                this.l10n_latam_identification_by_id[latam.id] = latam;
            }
        },
        save_l10n_latam_document: function (l10n_latam_document) {
            for (var i = 0; i < l10n_latam_document.length; i++) {
                var latam = l10n_latam_document[i];
                this.l10n_latam_document_by_id[latam.id] = latam;
            }
        },
    });

    return db;
});
