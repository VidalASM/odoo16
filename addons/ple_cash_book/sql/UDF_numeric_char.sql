CREATE or REPLACE FUNCTION UDF_numeric_char(value NUMERIC)
RETURNS VARCHAR
language plpgsql
as
$$
DECLARE
    value_res VARCHAR := ''; 
BEGIN
    value_res := trim(to_char(value, '9999999999.99'));
    IF split_part(value_res, '.', '1') = '' THEN
        value_res := CONCAT('0',value_res);		
    END IF;
    RETURN value_res;
END;
$$;