-- Create the staging schema
CREATE SCHEMA IF NOT EXISTS staging;

-- Create a raw_table for initial CSV load (match the columns in your CSV!)
CREATE TABLE IF NOT EXISTS staging.raw_table (
    project TEXT,
    subject TEXT,
    condition TEXT,
    age INTEGER,
    sex TEXT,
    treatment TEXT,
    response TEXT,
    sample TEXT,
    sample_type TEXT,
    time_from_treatment_start INTEGER,
    b_cell INTEGER,
    cd8_t_cell INTEGER,
    cd4_t_cell INTEGER,
    nk_cell INTEGER,
    monocyte INTEGER
);
