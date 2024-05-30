CREATE OR REPLACE FUNCTION get_journal_correlative(ple_type_contributor VARCHAR, ple_correlative VARCHAR)
RETURNS VARCHAR
language plpgsql
as
$$
DECLARE
    RES VARCHAR;
BEGIN
    IF ple_type_contributor = 'CUO' THEN 
        RES := COALESCE(ple_correlative, 'M000000001');
    ELSIF ple_type_contributor = 'RER' THEN
        RES := 'M-RER';
    ELSE 
        RES := '';
    END IF;
    
    RETURN RES;
END;
$$;