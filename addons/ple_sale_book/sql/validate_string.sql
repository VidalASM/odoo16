CREATE or REPLACE FUNCTION validate_string(value VARCHAR, max_len INTEGER)
-- Allows you to format a string without special characters and limit maximum characters
RETURNS VARCHAR
language plpgsql
as
$$
DECLARE
   new_value VARCHAR;
BEGIN
    IF value is NULL THEN
        new_value =  '';
    ELSE
        new_value = value;
        IF POSITION('-' IN value) != 0 THEN
            new_value = REPLACE(new_value, '-', '');
        END IF;
        IF POSITION('/' IN value) != 0 THEN
            new_value = REPLACE(new_value, '/', '');
        END IF;
        IF POSITION('\\n' IN value) != 0 THEN
            new_value = REPLACE(new_value, '\\n', '');
        END IF;
        IF POSITION('&' IN value) != 0 THEN
            new_value = REPLACE(new_value, '&', '');
        END IF;
        IF POSITION('á' IN value) != 0 THEN
            new_value = REPLACE(new_value, 'á', 'a');
        END IF;
        IF POSITION('é' IN value) != 0 THEN
            new_value = REPLACE(new_value, 'é', 'e');
        END IF;
        IF POSITION('í' IN value) != 0 THEN
            new_value = REPLACE(new_value, 'í', 'i');
        END IF;
        IF POSITION('ó' IN value) != 0 THEN
            new_value = REPLACE(new_value, 'ó', 'o');
        END IF;
        IF POSITION('ú' IN value) != 0 THEN
            new_value = REPLACE(new_value, 'ú', 'u');
        END IF;
        IF POSITION('ñ' IN value) != 0 THEN
            new_value = REPLACE(new_value, 'ñ', 'n-');
        END IF;
    END IF;
    IF max_len IS NOT NULL AND max_len != -1 THEN
        new_value = LEFT(new_value, max_len);
    END IF;
    RETURN new_value;
END;
$$;  