INSERT INTO staging.raw_table
SELECT * FROM read_csv_auto('@csv_path@');
