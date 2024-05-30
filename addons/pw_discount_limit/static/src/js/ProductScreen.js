odoo.define('pw_discount_limit.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const models = require('point_of_sale.models');
    const { _t } = require('web.core');

    const PosDiscountLimit = (ProductScreen) =>
        class extends ProductScreen {
            _setValue(val) {
                var selected_orderline = this.currentOrder.get_selected_orderline();
                if (selected_orderline && this.env.pos.config.restrict_discount) {
                    var product_id = selected_orderline.product;
                    var discount_limit = parseFloat(product_id.product_discount_limit || product_id.categ.discount_limit) || 0.0;
                    if (this.currentOrder.get_selected_orderline()) {
                        if (this.env.pos.numpadMode === 'quantity') {
                            const result = this.currentOrder.get_selected_orderline().set_quantity(val);
                            if (!result) NumberBuffer.reset();
                        }
                        else if (this.env.pos.numpadMode === 'discount') {
                            if (discount_limit && val > discount_limit){
                                this.showPopup('ErrorPopup', {
                                    title: this.env._t('Discount Restricted'),
                                    body: this.env._t('You cannot apply discount more than discount limit.'),
                                });
                                this.currentOrder.get_selected_orderline().set_discount(0);
                                NumberBuffer.reset();
                                return;
                            }
                            else {
                                this.currentOrder.get_selected_orderline().set_discount(val);
                            }
                        } else if (this.state.numpadMode === 'price') {
                            var selected_orderline = this.currentOrder.get_selected_orderline();
                            selected_orderline.price_manually_set = true;
                            selected_orderline.set_unit_price(val);
                        }
                    }
                }
                else {
                    super._setValue(val);
                }
            }
        };

    Registries.Component.extend(ProductScreen, PosDiscountLimit);

    return ProductScreen;
});
