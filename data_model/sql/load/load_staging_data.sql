INSERT INTO staging.raw_table
SELECT * FROM read_csv('@csv_path@',strict_mode='False');
