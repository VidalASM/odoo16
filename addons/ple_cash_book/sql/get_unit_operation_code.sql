CREATE or REPLACE FUNCTION get_unit_operation_code(account_move_id INTEGER)
-- Allows you to concatenate values of account_account_tag
RETURNS VARCHAR
language plpgsql
as
$$
DECLARE
    unit_operation_code VARCHAR := '';
    aml_line RECORD;
    aat_line RECORD;
BEGIN
    FOR aml_line IN (SELECT * FROM account_move_line WHERE move_id = account_move_id AND parent_state = 'posted') LOOP
        FOR aat_line IN (SELECT * FROM account_account_tag WHERE
            id in (SELECT account_account_tag_id FROM account_account_tag_account_move_line_rel
            WHERE account_move_line_id = aml_line.id)
        ) LOOP
            unit_operation_code := concat(unit_operation_code,'&',aat_line.name);
        END LOOP;
    END LOOP;
    RETURN unit_operation_code;
END;
$$;