CREATE or REPLACE FUNCTION get_tax_purchase(account_move_id INTEGER, move_type VARCHAR)
-- Allows you to calc amount by tax in all lines
RETURNS RECORD
language plpgsql
as
$$
DECLARE
    P_BASE_GDG NUMERIC := 0.0;
    P_TAX_GDG NUMERIC := 0.0;
    P_BASE_GDM NUMERIC := 0.0;
    P_TAX_GDM NUMERIC := 0.0;
    P_BASE_GDNG NUMERIC := 0.0;
    P_TAX_GDNG NUMERIC := 0.0;
    P_BASE_NG NUMERIC := 0.0;
    P_TAX_ISC NUMERIC := 0.0;
    P_TAX_ICBP NUMERIC := 0.0;
    P_TAX_OTHER NUMERIC := 0.0;
    AMOUNT_TOTAL NUMERIC := 0.0;
    tax_name VARCHAR := '';
    tax_amount NUMERIC;
    aml_line RECORD;
    tax_row_line RECORD;
    values RECORD;
BEGIN
    FOR aml_line IN (SELECT * FROM account_move_line WHERE move_id = account_move_id AND parent_state != 'cancel') LOOP
        FOR tax_row_line IN (SELECT * FROM account_account_tag WHERE 
            id IN (SELECT account_account_tag_id FROM account_account_tag_account_move_line_rel WHERE account_move_line_id = aml_line.id)
        ) LOOP
            tax_amount = 0.0;
            tax_amount = aml_line.balance ;
            tax_name = REPLACE(REPLACE(tax_row_line.name, '-', ''), '+', '');
            IF tax_name = 'P_BASE_GDG' THEN
                P_BASE_GDG := P_BASE_GDG + tax_amount;
            ELSIF tax_name = 'P_TAX_GDG' THEN
                P_TAX_GDG := P_TAX_GDG + tax_amount;
            ELSIF tax_name = 'P_BASE_GDM' THEN
                P_BASE_GDM := P_BASE_GDM + tax_amount;
            ELSIF tax_name = 'P_TAX_GDM' THEN
                P_TAX_GDM := P_TAX_GDM + tax_amount;
            ELSIF tax_name = 'P_BASE_GDNG' THEN
                P_BASE_GDNG := P_BASE_GDNG + tax_amount;
            ELSIF tax_name = 'P_TAX_GDNG' THEN
                P_TAX_GDNG := P_TAX_GDNG+ tax_amount;
            ELSIF tax_name = 'P_BASE_NG' THEN
                P_BASE_NG := P_BASE_NG + tax_amount;
            ELSIF tax_name = 'P_TAX_ISC' THEN
                P_TAX_ISC := P_TAX_ISC + tax_amount;
            ELSIF tax_name = 'P_TAX_ICBP' THEN
                P_TAX_ICBP := P_TAX_ICBP + tax_amount;
            ELSIF tax_name = 'P_TAX_OTHER' THEN
                P_TAX_OTHER := P_TAX_OTHER + tax_amount;
            ELSE
                tax_amount = 0.0;
            END IF;
            AMOUNT_TOTAL := AMOUNT_TOTAL + tax_amount;
        END LOOP;
    END LOOP;
    values := (ROUND(P_BASE_GDG, 2), ROUND(P_TAX_GDG, 2), ROUND(P_BASE_GDM, 2), ROUND(P_TAX_GDM, 2), ROUND(P_BASE_GDNG, 2),
               ROUND(P_TAX_GDNG,2), ROUND(P_BASE_NG, 2), ROUND(P_TAX_ISC, 2), ROUND(P_TAX_ICBP, 2), ROUND(P_TAX_OTHER, 2),
               ROUND(AMOUNT_TOTAL, 2));
    RETURN values;
END;
$$;