CREATE or REPLACE FUNCTION get_tax(account_move_id INTEGER, move_type VARCHAR, l10n_document_type_code VARCHAR)
-- Allows you to calc amount by tax in all lines 
RETURNS RECORD
language plpgsql
as
$$
DECLARE
    S_BASE_EXP NUMERIC := 0.0;
    S_BASE_OG NUMERIC := 0.0;
    S_BASE_OGD NUMERIC := 0.0;
    S_TAX_OG NUMERIC := 0.0;
    S_TAX_OGD NUMERIC := 0.0;
    S_BASE_OE NUMERIC := 0.0;
    S_BASE_OU NUMERIC := 0.0;
    S_TAX_ISC NUMERIC := 0.0;
    S_TAX_ICBP NUMERIC := 0.0;
    S_BASE_IVAP NUMERIC := 0.0;
    S_TAX_IVAP NUMERIC := 0.0;
    S_TAX_OTHER NUMERIC := 0.0;
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
            IF move_type in ('out_refund', 'out_invoice') THEN
                IF aml_line.balance < 0 THEN
                    tax_amount = ABS(aml_line.balance);
                ELSE
                    tax_amount = aml_line.balance * -1;
                END IF;
            ELSE
                tax_amount = aml_line.balance;
            END IF;
            tax_name = REPLACE(REPLACE(tax_row_line.name, '-', ''), '+', '');
            IF tax_name = 'S_BASE_EXP' THEN
                S_BASE_EXP := S_BASE_EXP + tax_amount;
            ELSIF tax_name = 'S_BASE_OG' THEN
                S_BASE_OG := S_BASE_OG + tax_amount;
            ELSIF tax_name = 'S_BASE_OGD' THEN
                S_BASE_OGD := S_BASE_OGD + tax_amount;
            ELSIF tax_name = 'S_TAX_OG' THEN
                S_TAX_OG := S_TAX_OG + tax_amount;
            ELSIF tax_name = 'S_TAX_OGD' THEN
                S_TAX_OGD := S_TAX_OGD + tax_amount;
            ELSIF tax_name = 'S_BASE_OE' THEN
                S_BASE_OE := S_BASE_OE + tax_amount;
            ELSIF tax_name = 'S_BASE_OU' THEN
                S_BASE_OU := S_BASE_OU + tax_amount;
            ELSIF tax_name = 'S_TAX_ISC' THEN
                S_TAX_ISC := S_TAX_ISC + tax_amount;
            ELSIF tax_name = 'S_TAX_ICBP' THEN
                S_TAX_ICBP := S_TAX_ICBP + tax_amount;
            ELSIF tax_name = 'S_BASE_IVAP' THEN
                S_BASE_IVAP := S_BASE_IVAP + tax_amount;
            ELSIF tax_name = 'S_TAX_IVAP' THEN
                S_TAX_IVAP := S_TAX_IVAP + tax_amount;
            ELSIF tax_name = 'S_TAX_OTHER' THEN
                S_TAX_OTHER := S_TAX_OTHER + tax_amount;
            ELSE
                tax_amount = 0.0;  
            END IF;
            AMOUNT_TOTAL := AMOUNT_TOTAL + tax_amount;
        END LOOP;
    END LOOP;
    values := (ROUND(S_BASE_EXP, 2), ROUND(S_BASE_OG, 2), ROUND(S_BASE_OGD, 2), ROUND(S_TAX_OG, 2), ROUND(S_TAX_OGD, 2), 
               ROUND(S_BASE_OE,2), ROUND(S_BASE_OU, 2), ROUND(S_TAX_ISC, 2), ROUND(S_TAX_ICBP, 2), ROUND(S_BASE_IVAP, 2), 
               ROUND(S_TAX_IVAP, 2), ROUND(S_TAX_OTHER, 2), ROUND(AMOUNT_TOTAL, 2));
    RETURN values;
END;
$$;