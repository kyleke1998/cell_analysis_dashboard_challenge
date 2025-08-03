import pandas as pd
import requests
import streamlit as st
import os
# Constants
API_URL = f"{os.getenv('API_HOST')}/analysis_results/relative_cell_frequency"
PAGE_SIZE = 50
# Set page config
st.set_page_config(page_title="Relative Cell Frequency Summary", layout="wide")

# Title
st.title("Relative Cell Frequency Summary")
st.markdown(
    """
This page shows the relative frequency of each immune cell type per sample.
For each sample, we calculate the total number of cells and the percentage breakdown across five cell populations.
"""
)

# Initialize session state for pagination
if "current_page" not in st.session_state:
    st.session_state.current_page = 1


# Fetch paginated data from API
def fetch_data(page: int, size: int = PAGE_SIZE):
    try:
        response = requests.get(API_URL, params={"page": page, "size": size})
        response.raise_for_status()
        data = response.json()
        return data["items"], data["total"]
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return [], 0


# Get data for the current page
data, total_items = fetch_data(st.session_state.current_page)

if data:
    df = pd.DataFrame(data)
    # change column names to more readable format
    df.columns = [col.replace("_", " ").title() for col in df.columns]
    st.dataframe(df, use_container_width=True)

    # Pagination controls
    total_pages = (total_items + PAGE_SIZE - 1) // PAGE_SIZE

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Previous", disabled=st.session_state.current_page == 1):
            st.session_state.current_page -= 1
            st.rerun()
    with col2:
        st.markdown(
            f"**Page {st.session_state.current_page} of {total_pages}**",
            unsafe_allow_html=True,
        )
    with col3:
        if st.button("Next", disabled=st.session_state.current_page >= total_pages):
            st.session_state.current_page += 1
            st.rerun()
else:
    st.info("No data available.")
