from . import models

from odoo import api, SUPERUSER_ID


def _refactor_xml(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    l10n_pe_template_base = env.ref('l10n_pe_edi.pe_ubl_2_1_common')
    for content in l10n_pe_template_base.inherit_children_ids:
        #aditional_document_reference
        if content.name == 'pe_ubl_2_1_invoice_body_inherit_l10n_pe_edocument_carrier_ref':
            new_content = '''
                        <data inherit_id="l10n_pe_edi.pe_ubl_2_1_common">
                                <xpath expr="//*[name()='cac:Signature']" position="before">
                                    <t xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
                                        <t t-if="record.carrier_ref_number and not record.exist_advance">
                                            <cac:DespatchDocumentReference>
                                                <cbc:ID t-esc="(str(record.carrier_ref_number).replace(' ', ''))[:30]"/>
                                                <cbc:DocumentTypeCode listAgencyName="PE:SUNAT"
                                                                      listName="Tipo de Documento"
                                                                      listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01">09</cbc:DocumentTypeCode>
                                            </cac:DespatchDocumentReference>
                                        </t>
                                    </t>
                                </xpath>
                            </data>
                        '''
            content.arch_base = new_content
        #carrier_reference_number_invoice
        if content.name == 'pe_ubl_2_1_invoice_aditional_document':
            new_content = '''
                        <data inherit_id="l10n_pe_edi.pe_ubl_2_1_common">
                                <xpath expr="//*[name()='cac:Signature']" position="before">
                                    <t xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
                                        <t t-if="record.aditional_document_reference">               
                                            <cac:AdditionalDocumentReference>
                                                <cbc:ID t-esc="record.aditional_document_reference"/>
                                                <cbc:DocumentTypeCode listAgencyName="PE:SUNAT" listName="Documento Relacionado" listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo12"
                                                    t-esc="record.related_tax_documents_code"/>
                                            </cac:AdditionalDocumentReference>
                                        </t>
                                    </t>
                                </xpath>
                            </data>
                        '''
            content.arch_base = new_content