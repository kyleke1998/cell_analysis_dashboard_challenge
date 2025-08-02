from db.connection import create_db_connection, DBConn
from db.crud import (
    fetch_boxplot_data,
    fetch_dynamic_subset_analysis,
    fetch_relative_cell_frequency,
)
from fastapi import FastAPI, HTTPException
from fastapi_pagination import add_pagination, Page, paginate
from rest.model_rest import (
    BoxPlotStatsResult,
    RelativeCellFrequencyResult,
    SubsetAnalysisResult,
)
from stat_tests import apply_mannwhitney_test, apply_t_test
from typing import Callable, Dict, List, Optional

import inject
import os
import yaml

# Load configuration from YAML
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "../..", "data")
CONFIG_PATH = f"{DATA_DIR}/duckdb_config.yaml"


def create_app(
    config_path: str, app_name: str, lifespan: Optional[Callable] = None
) -> FastAPI:
    """
    Creates and configures a FastAPI application.

    :param config_path: The path to the configuration file.
    :param app_name: The name of the application.
    :param lifespan: A callable object representing the lifespan of the application. Defaults to None.
    :return: FastAPI: The configured FastAPI application.
    """
    with open(config_path) as f:
        config = yaml.safe_load(f)

    inject.clear_and_configure(
        lambda binder: binder.bind(DBConn, create_db_connection(config))
    )
    app = FastAPI(lifespan=lifespan) if lifespan else FastAPI()

    # Define health check endpoint
    @app.get("/health")
    def health_check() -> Dict[str, str]:
        """
        Health check endpoint for the service.
        """
        return {"status": "healthy"}

    return app


app = create_app(CONFIG_PATH, app_name="Cell Count Analysis Service")
add_pagination(app)


@app.get("/analysis_results/relative_cell_frequency")
def get_relative_cell_frequency() -> Page[RelativeCellFrequencyResult]:
    """
    Retrieve relative cell frequency analysis results.

    Returns:
        Page[RelativeCellFrequencyResult]: Paginated relative cell frequency results.
    """
    try:
        # Fetch data from database
        df = fetch_relative_cell_frequency()
        results = df.to_dict("records")

        return paginate(results)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching relative cell frequency data: {str(e)}",
        )


@app.get("/analysis_results/boxplot_stats/{time_from_treatment_start}/{test_choice}")
def get_boxplot_stats(
    time_from_treatment_start: int, test_choice: str
) -> List[BoxPlotStatsResult]:
    """
    Retrieve box plot statistics for relative cell frequency analysis.
    Compares responder vs non-responder for  cell populations
    in PBMC samples from melanoma patients.

    Returns:
        List[BoxPlotStatsResult]: Box plot statistics results.
    """
    try:
        boxplot_df = fetch_boxplot_data(
            time_from_treatment_start=time_from_treatment_start
        )
        stats_test_raw_data = fetch_relative_cell_frequency(
            additional_filters=True, time_from_treatment_start=time_from_treatment_start
        )
        if test_choice == "mannwhitney":
            test_results = apply_mannwhitney_test(
                stats_test_raw_data, value_col="percentage"
            )
        elif test_choice == "t-test":
            test_results = apply_t_test(stats_test_raw_data, value_col="percentage")
        # Merge boxplot stats with statistical test results
        df = boxplot_df.merge(
            test_results, on=["population", "time_from_treatment_start"], how="left"
        )
        results = df.to_dict("records")
        return [BoxPlotStatsResult(**result) for result in results]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching box plot statistics data: {str(e)}"
        )


@app.get(
    "/analysis_results/subset_analysis/{treatment}/{condition}/{time_from_treatment_start}/{sample_type}",
    response_model=SubsetAnalysisResult,
)
def subset_analysis(
    treatment: str, condition: str, sample_type: str, time_from_treatment_start: int
):
    """
    Retrieve subset summary for specified sample and patient criteria:
    - Samples per project
    - Subject count by response
    - Subject count by sex
    """
    try:
        result_dict = fetch_dynamic_subset_analysis(
            treatment=treatment,
            condition=condition,
            sample_type=sample_type,
            time_from_treatment_start=time_from_treatment_start,
        )
        return result_dict
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching subset analysis data: {str(e)}"
        )
