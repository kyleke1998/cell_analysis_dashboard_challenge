import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import os
st.set_page_config(layout="wide")
st.title("Statistical Analysis")

API_URL = f"{os.getenv('API_HOST')}/analysis_results/boxplot_stats"
time_points = [0, 7, 14]

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Select Statistical Test")
    test_options = {
        "Mann-Whitney U Test": "mannwhitney",
        "T-Test (*Assumptions may not be met)": "t-test",
    }
    selected_test = st.selectbox("", options=list(test_options.keys()))
    test_choice = test_options[selected_test]

with col2:
    st.markdown("### 🕒 Select Time Since Treatment")
    selected_time = st.selectbox(
        "", options=time_points, format_func=lambda t: f"day {t}" if t != 0 else "day 0"
    )

response = requests.get(f"{API_URL}/{selected_time}/{test_choice}")
if response.status_code != 200:
    st.error("Failed to fetch data from backend.")
    st.stop()

data = response.json()
df = pd.DataFrame(data)

st.markdown(
    "#### Manhattan plot: *Significance of cell population differences between responders and non-responders of Miraclib*"
)


def make_manhattan_df(df):
    groups = df.groupby("population")
    manhattan_data = []
    for pop, group in groups:
        if group.shape[0] < 2:
            continue
        yes = group[group["response"] == "yes"]["avg_percentage"].values
        no = group[group["response"] == "no"]["avg_percentage"].values
        if len(yes) == 0 or len(no) == 0:
            continue
        adj_p = group["fdr_adj_p_val"].dropna().values
        raw_p = group["raw_p_value"].dropna().values
        manhattan_data.append(
            {
                "population": pop,
                "neg_log10_fdr": -np.log10(adj_p[0])
                if len(adj_p) > 0 and adj_p[0] > 0
                else np.nan,
                "fdr_adj_p_val": adj_p[0] if len(adj_p) > 0 else np.nan,
                "raw_p_value": raw_p[0] if len(raw_p) > 0 else np.nan,
            }
        )
    return pd.DataFrame(manhattan_data)


manhattan_df = make_manhattan_df(df)


def plot_manhattan(manhattan_df, sig_thresh=1.30103):
    manhattan_df["is_significant"] = manhattan_df["neg_log10_fdr"] > sig_thresh
    populations = list(manhattan_df["population"])
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=manhattan_df["population"],
            y=manhattan_df["neg_log10_fdr"],
            mode="markers+text",
            text=manhattan_df["population"],
            textposition="top center",
            marker=dict(
                size=16,
                color=np.where(manhattan_df["is_significant"], "#EF553B", "#636EFA"),
                line=dict(width=1, color="black"),
            ),
            hovertemplate="<b>%{text}</b><br>-log10(adj p): %{y:.2f}<br>adj p: %{customdata[0]:.3g}<br>raw p: %{customdata[1]:.3g}<extra></extra>",
            customdata=np.stack(
                [manhattan_df["fdr_adj_p_val"], manhattan_df["raw_p_value"]], axis=-1
            ),
        )
    )

    if len(populations) > 1:
        fig.add_shape(
            type="line",
            x0=populations[0],
            x1=populations[-1],
            y0=sig_thresh,
            y1=sig_thresh,
            line=dict(color="yellow", width=2, dash="dash"),
            xref="x",
            yref="y",
        )

    fig.update_layout(
        title="-log10(FDR-adjusted p-values) by Population (Significant above dashed line)",
        xaxis_title="Cell Population",
        yaxis_title="-log10(FDR adj p-value)",
        yaxis=dict(range=[0, max(2, manhattan_df["neg_log10_fdr"].max() + 0.5)]),
        width=900,
        height=450,
        showlegend=False,
        margin=dict(t=40, b=30),
        xaxis_tickangle=30,
    )
    return fig


st.plotly_chart(plot_manhattan(manhattan_df), use_container_width=True)

st.markdown("#### Box plots: *Compare cell population frequencies by response status*")

populations = list(df["population"].unique())
n = len(populations)
row_len = math.ceil(n / 3)
row1_pops = populations[:row_len]
row2_pops = populations[row_len : 2 * row_len]
row3_pops = populations[2 * row_len :]


def draw_summary_boxplot(fig, x, stats, color, label):
    fig.add_shape(
        type="rect",
        x0=x - 0.18,
        x1=x + 0.18,
        y0=stats["q1"],
        y1=stats["q3"],
        line=dict(color=color, width=2),
        fillcolor=color,
        opacity=0.25,
        layer="below",
    )
    fig.add_shape(
        type="line",
        x0=x - 0.18,
        x1=x + 0.18,
        y0=stats["median"],
        y1=stats["median"],
        line=dict(color=color, width=3),
    )
    fig.add_shape(
        type="line",
        x0=x,
        x1=x,
        y0=stats["min"],
        y1=stats["q1"],
        line=dict(color=color, width=2),
    )
    fig.add_shape(
        type="line",
        x0=x,
        x1=x,
        y0=stats["q3"],
        y1=stats["max"],
        line=dict(color=color, width=2),
    )
    fig.add_shape(
        type="line",
        x0=x - 0.10,
        x1=x + 0.10,
        y0=stats["min"],
        y1=stats["min"],
        line=dict(color=color, width=2),
    )
    fig.add_shape(
        type="line",
        x0=x - 0.10,
        x1=x + 0.10,
        y0=stats["max"],
        y1=stats["max"],
        line=dict(color=color, width=2),
    )
    fig.add_trace(
        go.Scatter(
            x=[x],
            y=[stats["median"]],
            mode="markers",
            marker=dict(symbol="diamond", size=10, color=color),
            showlegend=False,
            hovertemplate=(
                f"<b>{label}</b><br>"
                f"Median: {stats['median']}%<br>"
                f"Q1: {stats['q1']}%<br>"
                f"Q3: {stats['q3']}%<br>"
                f"Mean: {stats['avg']}%<extra></extra>"
            ),
        )
    )


def plot_box(pop, pop_df):
    fig = go.Figure()
    color_map = {"no": "#636EFA", "yes": "#EF553B"}
    label_map = {"no": "Non-Responder", "yes": "Responder"}
    x_map = {"no": 0, "yes": 1}
    y_min, y_max = float("inf"), float("-inf")
    legend_text = ""
    for resp in ["no", "yes"]:
        sub = pop_df[pop_df["response"] == resp]
        if not sub.empty:
            row = sub.iloc[0]
            min_val = row.get("lower_whisker", row["q1"])
            max_val = row.get("upper_whisker", row["q3"])
            stats = {
                "min": min_val,
                "q1": row["q1"],
                "median": row["median"],
                "q3": row["q3"],
                "max": max_val,
                "avg": row["avg_percentage"],
            }
            y_min = min(y_min, stats["min"])
            y_max = max(y_max, stats["max"])
            draw_summary_boxplot(
                fig, x_map[resp], stats, color_map[resp], label_map[resp]
            )
            if resp == "yes":
                pval = row.get("raw_p_value", None)
                adj_pval = row.get("fdr_adj_p_val", None)
                legend_text = (
                    (
                        f"<b>Raw p-value:</b> {pval:.3g}"
                        if pval is not None
                        else "Raw p-value: N/A"
                    )
                    + "<br>"
                    + (
                        f"<b>FDR-adjusted p-value:</b> {adj_pval:.3g}"
                        if adj_pval is not None
                        else "FDR-adjusted p-value: N/A"
                    )
                )
    fig.update_layout(
        title=pop.replace("_", " ").title(),
        yaxis_title="Relative Frequency (%)",
        xaxis=dict(
            tickvals=[0, 1], ticktext=["Non-Responder", "Responder"], range=[-0.5, 1.5]
        ),
        yaxis=dict(range=[max(y_min - 5, 0), y_max + 5]),
        width=800,
        height=450,
        margin=dict(t=40, b=30),
        font=dict(size=16),
        showlegend=False,
    )
    return fig, legend_text


def render_row(row_pops):
    cols = st.columns(len(row_pops))
    for idx, pop in enumerate(row_pops):
        pop_df = df[df["population"] == pop]
        fig, legend_text = plot_box(pop, pop_df)
        cols[idx].plotly_chart(fig, use_container_width=True)
        cols[idx].markdown(
            f'<div style="text-align:center; font-size:1rem; margin-bottom:1em;">{legend_text}</div>',
            unsafe_allow_html=True,
        )


render_row(row1_pops)
if row2_pops:
    render_row(row2_pops)
if row3_pops:
    render_row(row3_pops)
