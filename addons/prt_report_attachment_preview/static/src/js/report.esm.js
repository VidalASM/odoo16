/** @odoo-module **/

import {WARNING_MESSAGE, WKHTMLTOPDF_MESSAGES, _getReportUrl} from "./tools.esm";
import {_t} from "web.core";
import {registry} from "@web/core/registry";

/* eslint-disable init-declarations */
let wkhtmltopdfStateProm;
registry
    .category("ir.actions.report handlers")
    .add("open_report_handler", async function (action, options, env) {
        if (action.type === "ir.actions.report" && action.report_type === "qweb-pdf") {
            // Check the state of wkhtmltopdf before proceeding
            if (!wkhtmltopdfStateProm) {
                wkhtmltopdfStateProm = env.services.rpc("/report/check_wkhtmltopdf");
            }
            const state = await wkhtmltopdfStateProm;
            if (state in WKHTMLTOPDF_MESSAGES) {
                env.services.notification.add(WKHTMLTOPDF_MESSAGES[state], {
                    sticky: true,
                    title: _t("Report"),
                });
            }
            if (state === "upgrade" || state === "ok") {
                // Trigger the download of the PDF report
                const url = _getReportUrl(action, "pdf", env);
                // AAB: this check should be done in get_file service directly,
                // should not be the concern of the caller (and that way, get_file
                // could return a deferred)
                if (!window.open(url)) {
                    env.services.notification.add(WARNING_MESSAGE, {
                        type: "warning",
                    });
                } else if (action.close_on_report_download) {
                    env.services.action.doAction({
                        type: "ir.actions.act_window_close",
                    });
                }
            }
            return Promise.resolve(true);
        }
        return Promise.resolve(false);
    });
