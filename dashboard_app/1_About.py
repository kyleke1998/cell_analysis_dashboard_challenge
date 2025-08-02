from PIL import Image

import os
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="About",
    page_icon=":wave:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Load and display logo
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(CURRENT_DIR, "./images")
logo = Image.open(f"{IMAGE_DIR}/logo.jpeg")
st.image(logo, use_container_width=False, width=1000)


# Title
st.markdown("### Teiko Cell Analysis Dashboard", unsafe_allow_html=True)
# Description
st.markdown(
    """##### *This dashboard provides an interactive interface for analyzing immune cell count data from clinical trials.*"""
)


# Feature sections
st.markdown(
    '<div class="section-title">1. Relative Cell Frequency Summary</div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
View a summary table displaying the percentage of each immune cell type per sample.
For each sample, total cell counts are calculated and relative frequencies are shown for five immune populations
(e.g., B cells, CD4 T cells).
"""
)

st.markdown(
    '<div class="section-title">2. Statistical Analysis</div>', unsafe_allow_html=True
)
st.markdown(
    """
Compare immune cell frequencies between **responders** and **non-responders** to the drug *miraclib* in melanoma patients.
Includes boxplots and statistical significance testing.
"""
)

st.markdown(
    '<div class="section-title">3. Data Subset Exploration</div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
Filter and explore the dataset based on patient attributes and sample metadata.
Example queries include:
- How many baseline PBMC samples are from melanoma patients treated with miraclib?
- How are samples distributed across different projects or sex?
"""
)

# Footer
st.markdown("---")
st.markdown("**Developed by:** Kyle Ke  \n**Contact:** siyangke98@gmail.com")
