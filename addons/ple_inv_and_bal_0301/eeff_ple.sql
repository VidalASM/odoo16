-- This query is executed to copy the 'parent_id' data to the 'parent_ids' field
INSERT INTO eeff_ple_eeff_ple_rel (eeff_ple1_id, eeff_ple2_id)
    SELECT 
        eeff_ple.id AS eeff_ple, 
        eeff_ple.parent_id AS parent_id
    -- QUERIES TO MATCH MULTI TABLES
    FROM eeff_ple
    --  TYPE JOIN       |  TABLE                        | MATCH
    LEFT JOIN           eeff_ple_eeff_ple_rel           ON eeff_ple.id = eeff_ple_eeff_ple_rel.eeff_ple1_id
    -- FILTER QUERIES
    WHERE 
        eeff_ple.parent_id IS NOT NULL 
        AND eeff_ple_eeff_ple_rel.eeff_ple1_id IS NULL
        AND eeff_ple_eeff_ple_rel.eeff_ple2_id IS NULL;
