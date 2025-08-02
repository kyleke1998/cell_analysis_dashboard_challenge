from scipy.stats import false_discovery_control, mannwhitneyu, ttest_ind

import numpy as np
import pandas as pd


def _mannwhitney_test(g, value_col):
    """
    Perform Mann-Whitney U test between responders and non-responders.
    """
    r = g[g.response == "yes"][value_col].dropna()
    nr = g[g.response == "no"][value_col].dropna()
    if len(r) < 1 or len(nr) < 1:
        return np.nan
    return mannwhitneyu(r, nr)[1]


def apply_mannwhitney_test(df, value_col="percentage"):
    """
    Apply Mann-Whitney U test to the DataFrame grouped by 'time_from_treatment_start' and 'population'.
    """
    results = (
        df.groupby(["time_from_treatment_start", "population"])
        .apply(lambda g: _mannwhitney_test(g, value_col), include_groups=False)
        .reset_index()
    )
    results.columns = ["time_from_treatment_start", "population", "raw_p_value"]
    valid = ~results.raw_p_value.isna()
    results.loc[valid, "fdr_adj_p_val"] = false_discovery_control(
        results.loc[valid, "raw_p_value"]
    )
    results["neg_log_fdr_adj_p_val"] = -np.log10(results.fdr_adj_p_val.fillna(1))

    return results


def _t_test(g, value_col):
    """
    Perform two-sample t-test between responders and non-responders.
    """
    r = g[g.response == "yes"][value_col].dropna()
    nr = g[g.response == "no"][value_col].dropna()
    if len(r) < 1 or len(nr) < 1:
        return np.nan
    return ttest_ind(r, nr, equal_var=False).pvalue  # Welch’s t-test


def apply_t_test(df, value_col="percentage"):
    """
    Apply two-sample t-test to the DataFrame grouped by 'time_from_treatment_start' and 'population'.
    """
    results = (
        df.groupby(["time_from_treatment_start", "population"])
        .apply(lambda g: _t_test(g, value_col), include_groups=False)
        .reset_index()
    )
    results.columns = ["time_from_treatment_start", "population", "raw_p_value"]
    valid = ~results.raw_p_value.isna()
    results.loc[valid, "fdr_adj_p_val"] = false_discovery_control(
        results.loc[valid, "raw_p_value"]
    )
    results["neg_log_fdr_adj_p_val"] = -np.log10(results.fdr_adj_p_val.fillna(1))

    return results
