CREATE or REPLACE FUNCTION string_ref(value VARCHAR)
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
        new_value = replace(replace(replace(value,chr(10),''),chr(13),''),'                                ',' ');
    END IF;
RETURN new_value;
END;
$$;