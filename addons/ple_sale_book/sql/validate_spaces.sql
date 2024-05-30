CREATE or REPLACE FUNCTION validate_spaces(value VARCHAR)
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
        IF POSITION(' ' IN value) != 0 THEN
            new_value = REPLACE(new_value, ' ', '');
        END IF;
    END IF;
    RETURN new_value;
END;
$$;