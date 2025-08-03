import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import os
st.set_page_config(page_title="Treatment Subset Analysis", layout="wide")

st.title("Early Treatment Effect Analysis Dashboard")
st.subheader("Explore PBMC Samples by Subset Criteria")

st.markdown("#### 🔍 Filter Criteria")
col1, col2 = st.columns(2)

with col1:
    treatment = st.selectbox(
        "Select Treatment", options=["miraclib", "none", "phauximab"], index=0
    )
    time_from_treatment_start = st.selectbox(
        "Select Time from Treatment Start", options=[0, 7, 14], index=0
    )

with col2:
    condition = st.selectbox(
        "Select Condition", options=["melanoma", "carcinoma", "healthy"], index=0
    )
    sample_type = st.selectbox(
        "Select Sample Type", options=["PBMC", "WB"], index=0
    )

if (treatment == "none" and condition != "healthy") or (treatment != "none" and condition == "healthy"):
    st.error("Invalid selection: 'none' treatment must be paired with 'healthy' condition and vice versa.")
else:
    API_URL = f"{os.getenv('API_HOST')}/analysis_results/subset_analysis/{treatment}/{condition}/{time_from_treatment_start}/{sample_type}"

    # Fetch data
    with st.spinner("Fetching data..."):
        response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()

        st.markdown("### Samples per Project")
        df_samples = pd.DataFrame(data["samples_per_project"])
        st.dataframe(df_samples, use_container_width=True)

        st.markdown("### Subjects by Treatment Response")
        df_response = pd.DataFrame(data["subjects_by_response"])
        st.bar_chart(df_response.set_index("response"))

        st.markdown("### 🚻 Subjects by Sex")
        df_sex = pd.DataFrame(data["subjects_by_sex"])

        fig = px.pie(
            df_sex,
            names="sex",
            values="subject_count",
            title="Subjects by Sex Distribution",
            hole=0.3,
        )
        fig.update_traces(textinfo="label+value")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(f"API Request failed with status {response.status_code}: {response.text}")
