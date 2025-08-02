from pydantic import BaseModel
from typing import List, Literal, Optional


class RelativeCellFrequencyResult(BaseModel):
    """Model for the RelativeCellFrequencyResult endpoint."""

    sample: str
    total_count: int
    population: str
    count: int
    percentage: float


class BoxPlotStatsResult(BaseModel):
    """Model for the BoxPlotStatsResult endpoint."""

    population: str
    response: str
    time_from_treatment_start: int
    avg_percentage: float
    q1: float
    median: float
    q3: float
    iqr: float
    lower_whisker: float
    upper_whisker: float
    raw_p_value: Optional[float] = None
    fdr_adj_p_val: Optional[float] = None
    neg_log_fdr_adj_p_val: Optional[float] = None


class ProjectSampleCount(BaseModel):
    project: str
    sample_count: int


class SubjectCountByResponse(BaseModel):
    response: Literal["yes", "no", None]
    subject_count: int


class SubjectCountBySex(BaseModel):
    sex: Literal["M", "F", None]
    subject_count: int


class SubsetAnalysisResult(BaseModel):
    samples_per_project: List[ProjectSampleCount]
    subjects_by_response: List[SubjectCountByResponse]
    subjects_by_sex: List[SubjectCountBySex]
