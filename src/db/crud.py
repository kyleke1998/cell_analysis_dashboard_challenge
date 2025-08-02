from sqlalchemy import select, MetaData, Table, func
from sqlalchemy.engine import Engine
import pandas as pd
import inject
from db.connection import create_db_connection, DBConn
from db.constant import TableNames, SchemaNames
from typing import Optional
import os 


@inject.params(conn=DBConn)
def fetch_relative_cell_frequency(
    conn: DBConn,
    additional_filters: bool = False,
    time_from_treatment_start: Optional[int] = None
) -> pd.DataFrame:
    """
    Fetch relative cell frequency summary table from the database, with optional filtering.
    
    Args:
        conn: Database connection
        additional_filters: If True, apply melanoma PBMC filtering with joins
        time_from_treatment_start: If set, only include this timepoint
    """
    engine = conn.sqlalchemy_engine()
    metadata = MetaData()
    
    rcf = Table(TableNames.RELATIVE_CELL_FREQUENCY, metadata, autoload_with=engine, schema=SchemaNames.ANALYSIS)
    if additional_filters and time_from_treatment_start is not None:
        sp = Table(TableNames.SAMPLE, metadata, autoload_with=engine, schema=SchemaNames.ANALYSIS)
        subj = Table(TableNames.SUBJECT, metadata, autoload_with=engine, schema=SchemaNames.ANALYSIS)
        
        stmt = (
            select(
                rcf, 
                subj.c.response,
                sp.c.time_from_treatment_start
            )
            .select_from(
                rcf
                .join(sp, rcf.c.sample == sp.c.sample)
                .join(subj, sp.c.subject == subj.c.subject)
            )
            .where(
                sp.c.sample_type == 'PBMC',
                sp.c.time_from_treatment_start == time_from_treatment_start,
                subj.c.response.is_not(None),
                subj.c.condition == 'melanoma',
                subj.c.treatment == 'miraclib'
            )
        )
    else:
        stmt = select(rcf)    
    with engine.connect() as connection:
        result = connection.execute(stmt)
        return pd.DataFrame(result.fetchall(), columns=result.keys())


@inject.params(conn=DBConn)
def fetch_boxplot_data(conn: DBConn, time_from_treatment_start: int) -> pd.DataFrame:
    """
    Fetch box plot data for relative cell frequency analysis. Comparing responder vs non-responder
    for five major immune cell populations in PBMC samples from melanoma patients.
    """
    engine = conn.sqlalchemy_engine()
    metadata = MetaData()

    rcf = Table(TableNames.RELATIVE_CELL_FREQUENCY, metadata, autoload_with=engine, schema=SchemaNames.ANALYSIS)
    sp = Table(TableNames.SAMPLE, metadata, autoload_with=engine, schema=SchemaNames.ANALYSIS)
    subj = Table(TableNames.SUBJECT, metadata, autoload_with=engine, schema=SchemaNames.ANALYSIS)

    percentage = rcf.c.percentage
    q25 = func.quantile_cont(percentage, 0.25)
    q50 = func.median(percentage)
    q75 = func.quantile_cont(percentage, 0.75)
    iqr = q75 - q25
    lower_whisker = q25 - 1.5 * iqr
    upper_whisker = q75 + 1.5 * iqr

    stmt = (
        select(
            rcf.c.population,
            subj.c.response,
            sp.c.time_from_treatment_start,
            func.round(func.avg(percentage), 3).label("avg_percentage"),
            func.round(q25, 3).label("q1"),
            func.round(q50, 3).label("median"),
            func.round(q75, 3).label("q3"),
            func.round(iqr, 3).label("iqr"),
            func.round(lower_whisker, 3).label("lower_whisker"),
            func.round(upper_whisker, 3).label("upper_whisker"),
        )
        .select_from(
            rcf
            .join(sp, rcf.c.sample == sp.c.sample)
            .join(subj, sp.c.subject == subj.c.subject)
        )
        .where(
            sp.c.sample_type == 'PBMC',
            sp.c.time_from_treatment_start == time_from_treatment_start,
            subj.c.treatment == 'miraclib',
            subj.c.response.is_not(None),
            subj.c.condition == 'melanoma'
        )
        .group_by(
            rcf.c.population,
            subj.c.response,
            sp.c.time_from_treatment_start
        )
    )

    with engine.connect() as connection:
        result = connection.execute(stmt)
        return pd.DataFrame(result.fetchall(), columns=result.keys())


@inject.params(conn=DBConn)
def fetch_dynamic_subset_analysis(
    conn: DBConn,
    treatment: str = "miraclib",
    condition: str = "melanoma",
    sample_type: str = "PBMC",
    time_from_treatment_start: int = 0
) -> dict:
    """
    Perform dynamic subset analysis on biological sample data.

    This function filters the dataset based on user-specified parameters and returns
    a nested dictionary summarizing:
      - Number of samples per project
      - Number of subjects by treatment response 
      - Number of subjects by sex
    """
    engine = conn.sqlalchemy_engine()
    metadata = MetaData()

    sample = Table(TableNames.SAMPLE, metadata, autoload_with=engine, schema=SchemaNames.ANALYSIS)
    subject = Table(TableNames.SUBJECT, metadata, autoload_with=engine, schema=SchemaNames.ANALYSIS)

    joined = sample.join(subject, sample.c.subject == subject.c.subject)

    base_filters = [
        subject.c.condition == condition,
        subject.c.treatment == treatment,
        sample.c.sample_type == sample_type,
        sample.c.time_from_treatment_start == time_from_treatment_start,
    ]

    samples_per_project_stmt = (
        select(sample.c.project, func.count().label("sample_count"))
        .select_from(joined)
        .where(*base_filters)
        .group_by(sample.c.project)
    )

    response_stmt = (
        select(subject.c.response, func.count(func.distinct(subject.c.subject)).label("subject_count"))
        .select_from(joined)
        .where(*base_filters)
        .group_by(subject.c.response)
    )

    sex_stmt = (
        select(subject.c.sex, func.count(func.distinct(subject.c.subject)).label("subject_count"))
        .select_from(joined)
        .where(*base_filters)
        .group_by(subject.c.sex)
    )

    with engine.connect() as conn:
        samples_per_project = [
            {"project": row.project, "sample_count": row.sample_count}
            for row in conn.execute(samples_per_project_stmt)
        ]

        subjects_by_response = [
            {"response": row.response, "subject_count": row.subject_count}
            for row in conn.execute(response_stmt)
        ]

        subjects_by_sex = [
            {"sex": row.sex, "subject_count": row.subject_count}
            for row in conn.execute(sex_stmt)
        ]

    return {
        "samples_per_project": samples_per_project,
        "subjects_by_response": subjects_by_response,
        "subjects_by_sex": subjects_by_sex}
