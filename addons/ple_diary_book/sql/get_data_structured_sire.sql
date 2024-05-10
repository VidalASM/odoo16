CREATE OR REPLACE FUNCTION get_data_structured_sire(
    journal_type VARCHAR,
    journal_no_incluide_ple BOOLEAN,
    move_is_nodomicilied BOOLEAN,  
    move_name VARCHAR, 
    move_ref VARCHAR,
    company_vat VARCHAR,
    partner_vat VARCHAR,
    l10n_latam_document_type_code VARCHAR
)
RETURNS VARCHAR
language plpgsql
as
$$
DECLARE
    value_structured VARCHAR;

    move_name_serie VARCHAR;
    move_name_correlative VARCHAR;
    move_ref_serie VARCHAR;
    move_ref_correlative VARCHAR;
    move_partner_vat VARCHAR;
BEGIN
    value_structured := '';
    
    move_name_serie := LPAD(LEFT(COALESCE(SPLIT_PART(REPLACE(move_name, ' ', ''), '-', 1), ''), 4), 4, '0');
    move_name_correlative := LPAD(LEFT(COALESCE(SPLIT_PART(REPLACE(move_name, ' ', ''), '-', 2), ''), 10), 10, '0');
    move_ref_serie := LPAD(LEFT(COALESCE(SPLIT_PART(REPLACE(move_ref, ' ', ''), '-', 1), ''), 4), 4, '0');
    move_ref_correlative := LPAD(LEFT(COALESCE(SPLIT_PART(REPLACE(move_ref, ' ', ''), '-', 2), ''), 10), 10, '0');
    move_partner_vat := LPAD(LEFT(COALESCE(partner_vat, ''), 11), 11, '0');

    IF journal_type = 'sale' and (journal_no_incluide_ple = 'f' or journal_no_incluide_ple is null) THEN
        value_structured := CONCAT(company_vat, l10n_latam_document_type_code, move_name_serie, move_name_correlative); 
    ELSIF journal_type = 'purchase' and (journal_no_incluide_ple = 'f' or journal_no_incluide_ple is null) THEN
        IF move_is_nodomicilied = 'f' THEN
            value_structured := CONCAT(move_partner_vat, l10n_latam_document_type_code, move_ref_serie, move_ref_correlative);
        ELSE
            value_structured := CONCAT(move_partner_vat, l10n_latam_document_type_code, move_ref_serie, move_ref_correlative);
        END IF;                     
    END IF;
    
    RETURN value_structured;
END;
$$;