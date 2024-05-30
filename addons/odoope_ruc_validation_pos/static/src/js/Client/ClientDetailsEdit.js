odoo.define('odoope_ruc_validation_pos.ClientDetailsEdit', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ClientDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
    const Registries = require('point_of_sale.Registries');

    const RucValidationClientDetailsEdit = (ClientDetailsEdit) =>
        class extends ClientDetailsEdit {
            constructor() {
                super(...arguments);
            }

          
            async Ruc_DniData() {
                console.log(this.changes);
                let change = this.changes;
                if (change.vat){
                    if (!change.l10n_latam_identification_type_id){
                        return this.showPopup('ErrorPopup', {
                            title: _('Select the type of customer identification document and then write the number'),
                        });
                    }
                    var type_doc_model = this.env.pos.db.l10n_latam_identification_by_id[change.l10n_latam_identification_type_id];
                    if (type_doc_model.l10n_pe_vat_code === '6') {
                        this.props.partner['vat'] = change.vat;
                        this.props.partner['l10n_latam_identification_type_id'] = [type_doc_model.id, type_doc_model.name];
                        if (change.vat.length != 11){
                            return this.showPopup('ErrorPopup', {
                                title: _('The RUC of the client is not valid'),
                            });
                        };
                        let ruc_data = await this.rpc({ 
                            model: 'res.partner',
                            method: 'l10n_pe_ruc_connection',
                            args: [change.vat]
                        })
                        if (ruc_data) {
                            this.props.partner['name'] = ruc_data && ruc_data.business_name;
                            this.props.partner['street'] = ruc_data && ruc_data.residence;
                            this.changes['name'] = ruc_data && ruc_data.business_name;
                            this.changes['street'] = ruc_data && ruc_data.residence;
                            this.changes['country_id'] = ruc_data && ruc_data.country_id ;
                            this.changes['state_id'] =  ruc_data && ruc_data.state_id ;
                            this.render()
                        }else{
                            alert("NO HAY CONEXIÓN O LOS DATOS NO EXISTEN, POR FAVOR REGISTRE LOS DATOS MANUALMENTE.")
                        }
                    }
                    if (type_doc_model.l10n_pe_vat_code === '1') {
                        this.props.partner['vat'] = change.vat;
                        this.props.partner['l10n_latam_identification_type_id'] = [type_doc_model.id, type_doc_model.name];
                        if (change.vat.length != 8){
                            return this.showPopup('ErrorPopup', {
                                title: _('The DNI of the client is not valid'),
                            });
                        };
                        let dni_data = await this.rpc({ 
                            model: 'res.partner',
                            method: 'l10n_pe_dni_connection',
                            args: [change.vat],
                        });
                        if(dni_data){
                            this.props.partner['name'] = dni_data && dni_data.nombre;
                            this.changes['name'] = dni_data && dni_data.nombre;
                            this.render()
                        } else{
                            alert("NO HAY CONEXIÓN O LOS DATOS NO EXISTEN, POR FAVOR REGISTRE LOS DATOS MANUALMENTE.")
                        }
                    }
                }
                // console.log(this.props);
                // console.log(this.changes);
            }
            async dnival() {
                const change = this.changes;
                const dni_data = await this.rpc({ 
                    model: 'res.partner',
                    method: 'l10n_pe_dni_connection',
                    args: [change.vat],
                });
                if(dni_data){
                    this.props.partner['name'] = dni_data && dni_data.nombre;
                    this.props.partner['vat'] = change.vat;
                    this.props.partner['l10n_latam_identification_type_id'] = [type_doc_model.id, type_doc_model.name];
                    this.changes['name'] = dni_data && dni_data.nombre;
                    this.render()
                }
                console.log(this.props);
            }
            captureChange(event) {
                // console.log(event);
                this.changes[event.target.name] = event.target.value;
                console.log(this.changes);
                let change = this.changes;
                this.props.partner['vat'] = change.vat;
                // this.props.partner['l10n_latam_identification_type_id'] = change.l10n_latam_identification_type_id;
                // if (change.vat){
                //     var type_doc_model = this.env.pos.db.l10n_latam_identification_by_id[change.l10n_latam_identification_type_id];
                //     if (type_doc_model.l10n_pe_vat_code === '1') {
                //         this.props.partner['name'] = 'cambio';
                //     }
                // }
            }

        }
    Registries.Component.extend(ClientDetailsEdit, RucValidationClientDetailsEdit);

    return RucValidationClientDetailsEdit;
});
