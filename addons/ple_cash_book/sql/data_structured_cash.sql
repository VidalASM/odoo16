CREATE OR REPLACE FUNCTION data_structured_cash (
                        sc_id Char,
                        OUT ACCOUNT_MOVE_ID text) AS $$
BEGIN
SELECT 
CONCAT(
AM.ID,'**-**',
(CASE WHEN am.is_nodomicilied  IS True THEN 'T' ELSE 'F' END),'**-**',
aj.type, '**-**',
(CASE WHEN aj.ple_no_include is True THEN 'T' ELSE 'F' END),'**-**',
am.name,'**-**',
COALESCE(TO_CHAR(am.invoice_date, 'YYYYMM00'),''),'**-**'
) INTO ACCOUNT_MOVE_ID
FROM account_move am
LEFT JOIN account_move_line  aml ON  am.id=aml.move_id
LEFT JOIN account_journal  aj    ON  am.journal_id=aj.id
WHERE
aj.type in ('purchase','sale') and  aml.serie_correlative=sc_id
and aml.matching_number IS NOT NULL;
END;
$$ 
LANGUAGE plpgsql;