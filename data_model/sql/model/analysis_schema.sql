DROP TABLE IF EXISTS analysis.sample_cell_count;
DROP TABLE IF EXISTS analysis.sample;
DROP TABLE IF EXISTS analysis.subject;
DROP TABLE IF EXISTS analysis.project;

CREATE SCHEMA IF NOT EXISTS analysis;

CREATE TABLE analysis.project (
    project TEXT PRIMARY KEY,
    description TEXT
);

CREATE TABLE analysis.subject (
    subject TEXT PRIMARY KEY,
    condition TEXT,
    age INTEGER,
    sex TEXT,
    treatment TEXT,
    response TEXT
);

CREATE TABLE analysis.sample (
    sample TEXT PRIMARY KEY,
    subject TEXT,
    project TEXT,
    sample_type TEXT,
    time_from_treatment_start INTEGER,
    FOREIGN KEY (subject) REFERENCES analysis.subject(subject),
    FOREIGN KEY (project) REFERENCES analysis.project(project)
);

CREATE TABLE analysis.sample_cell_count (
    sample TEXT,
    population TEXT,
    count INTEGER,
    PRIMARY KEY (sample, population),
    FOREIGN KEY (sample) REFERENCES analysis.sample(sample)
);
