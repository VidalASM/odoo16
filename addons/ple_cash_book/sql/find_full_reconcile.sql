CREATE or REPLACE FUNCTION find_full_reconcile(full_reconcile_id INTEGER, entrada TEXT, salida VARCHAR)
RETURNS VARCHAR
language plpgsql
as
$$
DECLARE
BEGIN
    IF full_reconcile_id is not NULL THEN
        RETURN entrada;
    ELSE 
        RETURN salida;
    END IF;
END;
$$; 