-- Insert into analysis.project
INSERT OR IGNORE INTO analysis.project (project, description)
SELECT DISTINCT project, NULL
FROM staging.raw_table;

-- Insert into analysis.subject
INSERT INTO analysis.subject (subject, condition, age, sex, treatment, response)
SELECT DISTINCT
    subject, condition, age, sex, treatment, response
FROM staging.raw_table;

-- Insert into analysis.sample (metadata only)
INSERT INTO analysis.sample (
    sample, subject, project, sample_type, time_from_treatment_start
)
SELECT DISTINCT
    sample, subject, project, sample_type, time_from_treatment_start
FROM staging.raw_table;

-- Insert into analysis.sample_cell_count (long format)
INSERT INTO analysis.sample_cell_count (
    sample, population, count
)
SELECT sample, 'b_cell', b_cell FROM staging.raw_table
UNION ALL
SELECT sample, 'cd8_t_cell', cd8_t_cell FROM staging.raw_table
UNION ALL
SELECT sample, 'cd4_t_cell', cd4_t_cell FROM staging.raw_table
UNION ALL
SELECT sample, 'nk_cell', nk_cell FROM staging.raw_table
UNION ALL
SELECT sample, 'monocyte', monocyte FROM staging.raw_table;


-- Materialize relative cell frequency as a table
CREATE OR REPLACE TABLE analysis.relative_cell_frequency AS
WITH total_counts AS (
    SELECT sample, SUM(count) AS total_count
    FROM analysis.sample_cell_count
    GROUP BY sample
)
SELECT
    scc.sample,
    tc.total_count,
    scc.population,
    scc.count,
    ROUND(100.0 * scc.count / NULLIF(tc.total_count, 0), 2) AS percentage
FROM analysis.sample_cell_count scc
JOIN total_counts tc ON scc.sample = tc.sample;
DROP SCHEMA IF EXISTS staging CASCADE;
