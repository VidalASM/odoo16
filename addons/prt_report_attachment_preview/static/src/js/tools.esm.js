/** @odoo-module **/

import {_t} from "web.core";

export const _getReportUrl = (action, type, env) => {
    const url = new URL(
        `/report/${type}/${action.report_name}`,
        window.location.origin
    );
    const actionContext = action.context || {};
    if (action.data && JSON.stringify(action.data) !== "{}") {
        // Build a query string with `action.demo` (it's the place where reports
        // using a wizard to customize the output traditionally put their options)
        url.searchParams.set(
            "options",
            encodeURIComponent(JSON.stringify(action.data))
        );
        url.searchParams.set(
            "context",
            encodeURIComponent(JSON.stringify(actionContext))
        );
    } else {
        if (actionContext.active_ids) {
            url.pathname += `/${actionContext.active_ids.join(",")}`;
        }
        if (actionContext.allowed_company_ids) {
            const cid = actionContext.allowed_company_ids.join();
            url.searchParams.set("cid", cid);
        }
        if (type === "html") {
            /* eslint-disable no-undef */
            url.searchParams.set(
                "context",
                encodeURIComponent(JSON.stringify(env.services.user.context))
            );
        }
    }
    return url.toString();
};

const link =
    '<br><br><a href="http://wkhtmltopdf.org/" target="_blank">wkhtmltopdf.org</a>';

export const WKHTMLTOPDF_MESSAGES = {
    broken:
        _t(
            "Your installation of Wkhtmltopdf seems to be broken. The report will be shown " +
                "in html."
        ) + link,
    install:
        _t(
            "Unable to find Wkhtmltopdf on this system. The report will be shown in " +
                "html."
        ) + link,
    upgrade:
        _t(
            "You should upgrade your version of Wkhtmltopdf to at least 0.12.0 in order to " +
                "get a correct display of headers and footers as well as support for " +
                "table-breaking between pages."
        ) + link,
    workers: _t(
        "You need to start Odoo with at least two workers to print a pdf version of " +
            "the reports."
    ),
};

export const WARNING_MESSAGE = _t(
    "A popup window with your report was blocked. You " +
        "may need to change your browser settings to allow " +
        "popup windows for this page."
);
