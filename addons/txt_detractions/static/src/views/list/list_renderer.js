/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";

const formatters = registry.category("formatters");

export const patchTxtDetractionsListRenderer = {
    
    /** 
    *  @override
    **/
    get aggregates() {
        let values;
        if (this.props.list.selection && this.props.list.selection.length) {
            values = this.props.list.selection.map((r) => r.data);
        } else if (this.props.list.isGrouped) {
            values = this.props.list.groups.map((g) => g.aggregates);
        } else {
            values = this.props.list.records.map((r) => r.data);
        }
        const aggregates = {};
        for (const fieldName in this.props.list.activeFields) {
            const field = this.fields[fieldName];
            const fieldValues = values.map((v) => v[fieldName]).filter((v) => v || v === 0);
            if (!fieldValues.length) {
                continue;
            }
            const type = field.type;
            if (type !== "integer" && type !== "float" && type !== "monetary") {
                continue;
            }
            const { rawAttrs, widget } = this.props.list.activeFields[fieldName];
            let currencyId;
            const func =
                (rawAttrs.sum && "sum")     ||
                (rawAttrs.avg && "avg")     ||
                (rawAttrs.max && "max")     ||
                (rawAttrs.total && "total") ||
                (rawAttrs.min && "min");
            if ((type === "monetary" || widget === "monetary") && func !== "total") {
                const currencyField =
                    this.props.list.activeFields[fieldName].options.currency_field ||
                    this.fields[fieldName].currency_field ||
                    "currency_id";
                currencyId =
                    currencyField in this.props.list.activeFields &&
                    values[0][currencyField] &&
                    values[0][currencyField][0];
                if (currencyId) {
                    const sameCurrency = values.every(
                        (value) => currencyId === value[currencyField][0]
                    );
                    if (!sameCurrency) {
                        aggregates[fieldName] = {
                            help: this.env._t("Different currencies cannot be aggregated"),
                            value: "—",
                        };
                        continue;
                    }
                }
            }
            if (func) {
                let aggregateValue = 0;
                if (func === "max") {
                    aggregateValue = Math.max(-Infinity, ...fieldValues);
                } else if (func === "min") {
                    aggregateValue = Math.min(Infinity, ...fieldValues);
                } else if (func === "avg") {
                    aggregateValue =
                        fieldValues.reduce((acc, val) => acc + val) / fieldValues.length;
                } else if (func === "sum") {
                    aggregateValue = fieldValues.reduce((acc, val) => acc + val);
                } else if (func === "total") {
                    aggregateValue = fieldValues.reduce((acc, val) => acc + val);
                }
                const formatter = formatters.get(widget, false) || formatters.get(type, false);
                const formatOptions = {
                    digits: rawAttrs.digits ? JSON.parse(rawAttrs.digits) : undefined,
                    escape: true,
                };
                if (currencyId) {
                    formatOptions.currencyId = currencyId;
                }
                aggregates[fieldName] = {
                    help: rawAttrs[func],
                    value: formatter ? formatter(aggregateValue, formatOptions) : aggregateValue,
                };
            }
        }
        return aggregates;
    }
};
patch(ListRenderer.prototype, "txt_detractions.TxtDetractionsListRenderer", patchTxtDetractionsListRenderer);