from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result += [
            "l10n_latam.identification.type",
            "l10n_latam.document.type",
            "l10n_pe_edi.supplier",
            "account.journal",
            "res.config.settings",
            "pos.receipt",
        ]
        return result

    def _loader_params_l10n_latam_identification_type(self):
        return {"search_params": {"domain": [], "fields": ["name", "l10n_pe_vat_code"]}}

    def _get_pos_ui_l10n_latam_identification_type(self, params):
        return self.env["l10n_latam.identification.type"].search_read(
            **params["search_params"]
        )

    def _loader_params_res_partner(self):
        params = super()._loader_params_res_partner()
        params["search_params"]["fields"].append("l10n_latam_identification_type_id")
        return params

    def _loader_params_l10n_latam_document_type(self):
        return {"search_params": {"domain": [], "fields": ["name", "code"]}}

    def _get_pos_ui_l10n_latam_document_type(self, params):
        return self.env["l10n_latam.document.type"].search_read(
            **params["search_params"]
        )

    def _loader_params_l10n_pe_edi_supplier(self):
        return {
            "search_params": {
                "domain": [],
                "fields": ["name", "control_url", "authorization_message", "code"],
            }
        }

    def _get_pos_ui_l10n_pe_edi_supplier(self, params):
        return self.env["l10n_pe_edi.supplier"].search_read(**params["search_params"])

    def _loader_params_account_journal(self):
        return {
            "search_params": {
                "domain": [("id", "in", self.config_id.invoice_journal_ids.ids)],
                "fields": [
                    "name",
                    "l10n_latam_document_type_id",
                    "display_name",
                    "l10n_document_internal_type",
                ],
            }
        }

    def _get_pos_ui_account_journal(self, params):
        return self.env["account.journal"].search_read(**params["search_params"])

    def _loader_params_pos_receipt(self):
        return {
            "search_params": {
                "fields": ["design_receipt", "name"],
            },
        }

    def _get_pos_ui_pos_receipt(self, params):
        return self.env["pos.receipt"].search_read(**params["search_params"])

    def _loader_params_res_config_settings(self):
        return {
            "search_params": {
                "fields": ["pos_receipt_design"],
            },
        }

    def _get_pos_ui_res_config_settings(self, params):
        return self.env["res.config.settings"].search_read(**params["search_params"])

    def _loader_params_res_company(self):
        params = super()._loader_params_res_company()
        params["search_params"]["fields"].extend(
            ["street", "l10n_pe_edi_ose_id", "l10n_pe_edi_send_invoice"]
        )
        return params
