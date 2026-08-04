import json
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "SGJobData_cleaned.csv")

# Palette (validated categorical set, fixed order — see dataviz skill)
CATEGORICAL_PALETTE = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]
OTHER_COLOR = "#898781"  # muted gray, reserved for the "Other" bucket
TEXT_PRIMARY = "#0b0b0b"
SURFACE = "#fcfcfb"
PIE_TOP_N = 8

TABLE_COLS = [
    "postedCompany_name",
    "positionLevels",
    "title",
    "numberOfVacancies",
    "employmentTypes",
    "minimumYearsExperience",
    "salary_maximum",
    "salary_minimum",
    "average_salary",
    "metadata_jobPostId",
    "metadata_totalNumberJobApplication",
    "metadata_totalNumberOfView",
]

LOAD_COLS = [
    "postedCompany_name",
    "positionLevels",
    "title",
    "numberOfVacancies",
    "salary_maximum",
    "salary_minimum",
    "average_salary",
    "employmentTypes",
    "categories",
    "minimumYearsExperience",
    "status_jobStatus",
    "metadata_isPostedOnBehalf",
    "metadata_jobPostId",
    "metadata_totalNumberJobApplication",
    "metadata_totalNumberOfView",
]

JOB_STATUS_ORDER = ["Open", "Re-open", "Closed"]

st.set_page_config(page_title="SG Job Postings Dashboard", layout="wide")


@st.cache_data(show_spinner="Loading job data...")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=LOAD_COLS)

    df["categories"] = df["categories"].astype("string").str.strip()
    df["category_names"] = df["categories"].apply(
        lambda x: [c["category"] for c in json.loads(x)] if x else []
    )
    df = df.drop(columns=["categories"])

    return df


df = load_data(CSV_PATH)

st.title("SG Job Postings Dashboard")
st.caption("Filter job postings on the left to explore matching roles.")

# ---- Sidebar filters ----
st.sidebar.header("Filters")

sal_min_bound = int(df["salary_minimum"].min())
sal_min_upper = int(df["salary_minimum"].max())
salary_minimum_floor = st.sidebar.number_input(
    "Salary minimum (at least)",
    min_value=sal_min_bound,
    max_value=sal_min_upper,
    value=sal_min_bound,
    step=100,
)
st.sidebar.caption(f"${salary_minimum_floor:,}")

sal_max_bound = int(df["salary_maximum"].min())
sal_max_upper = int(df["salary_maximum"].max())
salary_maximum_ceiling = st.sidebar.number_input(
    "Salary maximum (at most)",
    min_value=sal_max_bound,
    max_value=sal_max_upper,
    value=sal_max_upper,
    step=100,
)
st.sidebar.caption(f"${salary_maximum_ceiling:,}")

avg_sal_bound = int(df["average_salary"].min())
avg_sal_upper = int(df["average_salary"].max())
average_salary_floor = st.sidebar.number_input(
    "Average salary (at least)",
    min_value=avg_sal_bound,
    max_value=avg_sal_upper,
    value=avg_sal_bound,
    step=100,
)
st.sidebar.caption(f"${average_salary_floor:,}")

employment_types = sorted(df["employmentTypes"].dropna().unique())
selected_employment_types = st.sidebar.multiselect(
    "Employment types", options=employment_types, default=[]
)

all_categories = sorted({c for cats in df["category_names"] for c in cats})
selected_categories = st.sidebar.multiselect(
    "Categories", options=all_categories, default=[]
)

position_levels = sorted(df["positionLevels"].dropna().unique())
selected_position_levels = st.sidebar.multiselect(
    "Position levels", options=position_levels, default=[]
)

exp_bound = int(df["minimumYearsExperience"].min())
exp_upper = int(df["minimumYearsExperience"].max())
minimum_experience = st.sidebar.number_input(
    "Minimum years experience (at least)",
    min_value=exp_bound,
    max_value=exp_upper,
    value=exp_bound,
    step=1,
)
maximum_experience = st.sidebar.number_input(
    "Minimum years experience (at most)",
    min_value=exp_bound,
    max_value=exp_upper,
    value=exp_upper,
    step=1,
)

present_statuses = set(df["status_jobStatus"].dropna().unique())
job_statuses = [s for s in JOB_STATUS_ORDER if s in present_statuses] + sorted(
    present_statuses - set(JOB_STATUS_ORDER)
)
selected_job_statuses = st.sidebar.multiselect(
    "Job status", options=job_statuses, default=[]
)

posted_on_behalf = st.sidebar.selectbox(
    "Posted on behalf", options=["All", "True", "False"], index=0
)

# ---- Apply filters ----
mask = pd.Series(True, index=df.index)
mask &= df["salary_minimum"] >= salary_minimum_floor
mask &= df["salary_maximum"] <= salary_maximum_ceiling
mask &= df["minimumYearsExperience"] >= minimum_experience
mask &= df["minimumYearsExperience"] <= maximum_experience
mask &= df["average_salary"] >= average_salary_floor

if selected_employment_types:
    mask &= df["employmentTypes"].isin(selected_employment_types)

if selected_categories:
    mask &= df["category_names"].apply(
        lambda cats: any(c in selected_categories for c in cats)
    )

if selected_position_levels:
    mask &= df["positionLevels"].isin(selected_position_levels)

if selected_job_statuses:
    mask &= df["status_jobStatus"].isin(selected_job_statuses)

if posted_on_behalf != "All":
    mask &= df["metadata_isPostedOnBehalf"] == (posted_on_behalf == "True")

filtered = df.loc[mask, TABLE_COLS].reset_index(drop=True)

# ---- KPI row ----
total_vacancies = filtered["numberOfVacancies"].sum()
weighted_avg_salary = (
    (filtered["average_salary"] * filtered["numberOfVacancies"]).sum() / total_vacancies
    if total_vacancies
    else None
)

total_applications = filtered["metadata_totalNumberJobApplication"].sum()
total_views = filtered["metadata_totalNumberOfView"].sum()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Matching postings", f"{len(filtered):,}")
col2.metric(
    "Average salary",
    f"${weighted_avg_salary:,.0f}" if weighted_avg_salary is not None else "—",
)
col3.metric("Companies", f"{filtered['postedCompany_name'].nunique():,}")
col4.metric("Total job applications", f"{total_applications:,.0f}")
col5.metric("Total views", f"{total_views:,.0f}")
col6.metric("Total vacancies", f"{total_vacancies:,.0f}")

st.divider()

# ---- Pie charts ----
st.subheader("Breakdown of matching postings")


def make_pie(series: pd.Series, title: str) -> go.Figure:
    counts = series.dropna().value_counts()
    if len(counts) > PIE_TOP_N:
        top = counts.iloc[:PIE_TOP_N]
        other_total = counts.iloc[PIE_TOP_N:].sum()
        counts = pd.concat([top, pd.Series({"Other": other_total})])

    colors = CATEGORICAL_PALETTE[: len(counts)]
    if "Other" in counts.index:
        colors = colors[: len(counts) - 1] + [OTHER_COLOR]

    total = counts.sum()
    legend_labels = [
        f"{name} — {value / total:.1%} ({value:,})"
        for name, value in counts.items()
    ]

    fig = go.Figure(
        go.Pie(
            labels=legend_labels,
            values=counts.values,
            marker=dict(colors=colors, line=dict(color=SURFACE, width=2)),
            textinfo="none",
            hovertext=counts.index,
            hovertemplate="%{hovertext}<br>%{percent} — %{value:,} postings<extra></extra>",
            sort=False,
        )
    )
    fig.update_layout(
        title=title,
        height=420,
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font=dict(color=TEXT_PRIMARY, family="system-ui, -apple-system, sans-serif"),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="v", yanchor="middle", y=0.5, font=dict(size=11)),
    )
    return fig


if len(filtered):
    pie_col1, pie_col2 = st.columns(2)
    with pie_col1:
        st.plotly_chart(
            make_pie(filtered["positionLevels"], "Position level"),  use_container_width=True
            #width="stretch"
        )
    with pie_col2:
        st.plotly_chart(
            make_pie(filtered["employmentTypes"], "Employment type"), width="stretch"
        )
else:
    st.info("No postings match the current filters.")

# ---- Main table ----
st.divider()
st.subheader("Job postings")

table_col1, table_col2 = st.columns([3, 1])
title_search = table_col1.text_input("Filter by title contains", value="", placeholder="e.g. engineer")
show_job_post_id = table_col2.checkbox("Show Job Post ID", value=False)

if title_search:
    filtered = filtered[filtered["title"].str.contains(title_search, case=False, na=False)]

table_column_order = [
    "postedCompany_name",
    "positionLevels",
    "title",
    "numberOfVacancies",
    "employmentTypes",
    "minimumYearsExperience",
    "salary_maximum",
    "salary_minimum",
    "average_salary",
]
if show_job_post_id:
    table_column_order.append("metadata_jobPostId")

st.dataframe(
    filtered,
    #width="stretch", 
    use_container_width=True,
    hide_index=True,
    column_order=table_column_order,
    column_config={
        "postedCompany_name": st.column_config.TextColumn("Company"),
        "positionLevels": st.column_config.TextColumn("Position level"),
        "title": st.column_config.TextColumn("Title", width="large"),
        "numberOfVacancies": st.column_config.NumberColumn("Vacancies", format="%d"),
        "employmentTypes": st.column_config.TextColumn("Employment type"),
        "minimumYearsExperience": st.column_config.NumberColumn("Min. years experience", format="%d"),
        "salary_maximum": st.column_config.NumberColumn("Salary max", format="$%,d"),
        "salary_minimum": st.column_config.NumberColumn("Salary min", format="$%,d"),
        "average_salary": st.column_config.NumberColumn("Avg salary", format="$%,.0f"),
        "metadata_jobPostId": st.column_config.TextColumn("Job Post ID"),
    },
)
