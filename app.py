import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

CSV_PATH = "SGJobData.csv"


# Palette (validated categorical/sequential set — see dataviz skill)
BLUE = "#2a78d6"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
MUTED = "#898781"
GRIDLINE = "#e1e0d9"

st.set_page_config(page_title="SG Job Postings — Category Map", layout="wide")


JOB_ATTR_COLS = [
    "positionLevels",
    "postedCompany_name",
    "salary_type",
    "salary_minimum",
    "salary_maximum",
    "average_salary",
]


@st.cache_data(show_spinner="Loading job data...")
def load_df_map(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["metadata_jobPostId", "categories", *JOB_ATTR_COLS])
    df["categories"] = df["categories"].astype("string").str.strip()
    df = df[df["categories"].notna() & (df["categories"] != "")]

    df["categories"] = df["categories"].apply(json.loads)

    df_map = df.explode("categories").reset_index(drop=True)
    df_map = df_map.dropna(subset=["categories"])
    df_map["category_id"] = df_map["categories"].apply(lambda x: x["id"])
    df_map["category_name"] = df_map["categories"].apply(lambda x: x["category"])
    df_map = df_map.drop(columns=["categories"])
    return df_map


df_map = load_df_map(CSV_PATH)

st.title("SG Job Postings — Category Map")
st.caption("Built from `df_map`: each row links a job posting to one category it was tagged with.")

# ---- Sidebar filters ----
all_categories = sorted(df_map["category_name"].unique())
selected_categories = st.sidebar.multiselect(
    "Category", options=all_categories, default=[]
)

all_position_levels = sorted(df_map["positionLevels"].dropna().unique())
selected_position_levels = st.sidebar.multiselect(
    "Position level", options=all_position_levels, default=[]
)

all_salary_types = sorted(df_map["salary_type"].dropna().unique())
selected_salary_types = st.sidebar.multiselect(
    "Salary type", options=all_salary_types, default=[]
)

company_search = st.sidebar.text_input("Company name contains")

sal_min_bound = int(df_map["salary_minimum"].min())
sal_max_bound = int(df_map["salary_minimum"].max())
salary_minimum_range = st.sidebar.slider(
    "Salary minimum", min_value=sal_min_bound, max_value=sal_max_bound,
    value=(sal_min_bound, sal_max_bound),
)

max_min_bound = int(df_map["salary_maximum"].min())
max_max_bound = int(df_map["salary_maximum"].max())
salary_maximum_range = st.sidebar.slider(
    "Salary maximum", min_value=max_min_bound, max_value=max_max_bound,
    value=(max_min_bound, max_max_bound),
)

avg_min_bound = int(df_map["average_salary"].min())
avg_max_bound = int(df_map["average_salary"].max())
average_salary_range = st.sidebar.slider(
    "Average salary", min_value=avg_min_bound, max_value=avg_max_bound,
    value=(avg_min_bound, avg_max_bound),
)

top_n = st.sidebar.slider("Categories to show in chart", min_value=5, max_value=40, value=15)

mask = pd.Series(True, index=df_map.index)
if selected_categories:
    mask &= df_map["category_name"].isin(selected_categories)
if selected_position_levels:
    mask &= df_map["positionLevels"].isin(selected_position_levels)
if selected_salary_types:
    mask &= df_map["salary_type"].isin(selected_salary_types)
if company_search:
    mask &= df_map["postedCompany_name"].str.contains(company_search, case=False, na=False)
mask &= df_map["salary_minimum"].between(*salary_minimum_range)
mask &= df_map["salary_maximum"].between(*salary_maximum_range)
mask &= df_map["average_salary"].between(*average_salary_range)

filtered = df_map[mask]

# ---- KPI row ----
col1, col2, col3 = st.columns(3)
col1.metric("Job postings", f"{df_map['metadata_jobPostId'].nunique():,}")
col2.metric("Distinct categories", f"{df_map['category_id'].nunique():,}")
col3.metric("Category assignments", f"{len(df_map):,}")

st.divider()

# ---- Bar chart: top categories by job count ----
counts = (
    filtered.groupby("category_name")["metadata_jobPostId"]
    .nunique()
    .sort_values(ascending=False)
    .head(top_n)
    .sort_values(ascending=True)
)

fig = go.Figure(
    go.Bar(
        x=counts.values,
        y=counts.index,
        orientation="h",
        marker=dict(color=BLUE, cornerradius=4),
        hovertemplate="%{y}<br>%{x:,} job postings<extra></extra>",
    )
)
fig.update_layout(
    title=f"Top {top_n} categories by job postings",
    height=max(400, 24 * top_n),
    plot_bgcolor="#fcfcfb",
    paper_bgcolor="#fcfcfb",
    font=dict(color=TEXT_PRIMARY, family="system-ui, -apple-system, sans-serif"),
    xaxis=dict(title="Job postings", gridcolor=GRIDLINE, zeroline=False, color=MUTED),
    yaxis=dict(title=None, color=TEXT_SECONDARY),
    margin=dict(l=10, r=10, t=50, b=40),
)
st.plotly_chart(fig, width="stretch")

# ---- Table ----
st.subheader("Category counts")
table = (
    filtered.groupby(["category_id", "category_name"])["metadata_jobPostId"]
    .nunique()
    .reset_index(name="job_postings")
    .sort_values("job_postings", ascending=False)
    .reset_index(drop=True)
)
st.dataframe(table, width="stretch", hide_index=True)

with st.expander("Underlying job ↔ category rows"):
    st.dataframe(filtered.reset_index(drop=True), width="stretch", hide_index=True)
