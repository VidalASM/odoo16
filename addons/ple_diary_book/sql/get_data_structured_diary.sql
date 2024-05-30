CREATE OR REPLACE FUNCTION get_data_structured_diary(journal_type VARCHAR,journal_no_incluide_ple BOOLEAN, move_is_nodomicilied BOOLEAN,  move_name VARCHAR, move_date DATE)
RETURNS VARCHAR
language plpgsql
as
$$
DECLARE
    value_structured VARCHAR;
    move_date_char VARCHAR;
    move_name_parse VARCHAR;
BEGIN
    value_structured := '';
    move_date_char := TO_CHAR(move_date, 'YYYYMM');
    move_name_parse := replace(replace(replace(move_name, '/', ''), '-', ''), ' ', '');
    
    IF journal_type = 'sale' and (journal_no_incluide_ple = 'f' or journal_no_incluide_ple is null) THEN
        value_structured := CONCAT('140100&', move_date_char, '00&', move_name_parse, '&M000000001'); 
    
    ELSIF journal_type = 'purchase' and (journal_no_incluide_ple = 'f' or journal_no_incluide_ple is null) THEN
        
        IF move_is_nodomicilied = 'f' THEN
            value_structured := CONCAT('080100&', move_date_char, '00&', move_name_parse, '&M000000001');
        ELSE
            value_structured := CONCAT('080200&', move_date_char, '00&', move_name_parse, '&M000000001');
        END IF;                     
        
    END IF;
    
    RETURN value_structured;
END;
$$;