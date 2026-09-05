
# Install:
# python -m pip install streamlit pandas openpyxl plotly
#
# Run:
# python -m streamlit run shooter_dashboard.py


import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date


# ============================================================
# Configuration
# ============================================================

EXCEL_FILE = "example_david.xlsx"


# ============================================================
# Streamlit page configuration
# ============================================================

st.set_page_config(
    page_title="USPSA Shooter Dashboard",
    page_icon="🎯",
    layout="wide",
)


# ============================================================
# Load Excel data
# ============================================================

@st.cache_data
def load_data(file_path):

    df = pd.read_excel(file_path)

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = df.columns.astype(str).str.strip()

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required_columns = [
        "match_date",
        "%",
        "Div",
        "match_name",
        "Name",
    ]

    missing_columns = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    # --------------------------------------------------------
    # Convert match date
    # --------------------------------------------------------

    df["match_date"] = pd.to_datetime(
        df["match_date"],
        errors="coerce",
    )

    # --------------------------------------------------------
    # Convert percentage to numeric
    # --------------------------------------------------------

    df["%"] = pd.to_numeric(
        df["%"],
        errors="coerce",
    )

    # --------------------------------------------------------
    # Clean Division
    # --------------------------------------------------------

    df["Div"] = (
        df["Div"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Clean match name
    # --------------------------------------------------------

    df["match_name"] = (
        df["match_name"]
        .fillna("Unknown Match")
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Clean shooter name
    # --------------------------------------------------------

    df["Name"] = (
        df["Name"]
        .fillna("Unknown Shooter")
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Remove invalid rows
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "match_date",
            "%",
        ]
    ).copy()

    # --------------------------------------------------------
    # Handle percentage format
    #
    # 85.5  -> 85.5%
    # 0.855 -> 85.5%
    # --------------------------------------------------------

    if not df.empty and df["%"].max() <= 1:
        df["%"] = df["%"] * 100

    # --------------------------------------------------------
    # Normalize match_date to pandas datetime
    # --------------------------------------------------------

    df["match_date"] = pd.to_datetime(
        df["match_date"],
        errors="coerce",
    )

    # Remove anything that became invalid after conversion
    df = df.dropna(
        subset=["match_date", "%"]
    ).copy()

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    df = (
        df
        .sort_values("match_date")
        .reset_index(drop=True)
    )

    return df


# ============================================================
# Load data
# ============================================================

try:

    df = load_data(EXCEL_FILE)

except FileNotFoundError:

    st.error(
        f"Could not find `{EXCEL_FILE}`.\n\n"
        "Make sure the Excel file is in the same "
        "directory as `shooter_dashboard.py`."
    )

    st.stop()

except Exception as e:

    st.error(
        f"Error loading Excel file:\n\n{e}"
    )

    st.stop()


# ============================================================
# Check for empty data
# ============================================================

if df.empty:

    st.error(
        "No valid match data was found in the Excel file."
    )

    st.stop()


# ============================================================
# Sidebar
# ============================================================

st.sidebar.title("🎯 Dashboard Filters")


# ============================================================
# Division filter
# ============================================================

divisions = sorted(
    df["Div"]
    .dropna()
    .unique()
    .tolist()
)

selected_divisions = st.sidebar.multiselect(
    "Division",
    options=divisions,
    default=divisions,
)


# ============================================================
# Date filter
# ============================================================

min_date = df["match_date"].min().date()
max_date = df["match_date"].max().date()

selected_dates = st.sidebar.date_input(
    "Match Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)


# ============================================================
# Apply filters
# ============================================================

filtered_df = df[
    df["Div"].isin(selected_divisions)
].copy()


# ============================================================
# Date filtering
# ============================================================

if (
    isinstance(selected_dates, (tuple, list))
    and len(selected_dates) == 2
):

    start_date = selected_dates[0]
    end_date = selected_dates[1]

    filtered_df = filtered_df[
        (
            filtered_df["match_date"].dt.date
            >= start_date
        )
        &
        (
            filtered_df["match_date"].dt.date
            <= end_date
        )
    ].copy()

elif isinstance(selected_dates, date):

    filtered_df = filtered_df[
        filtered_df["match_date"].dt.date
        == selected_dates
    ].copy()


# ============================================================
# Dashboard title
# ============================================================

st.title("🎯 USPSA Shooter Performance Dashboard")

st.markdown(
    "Performance percentage over time, grouped by USPSA Division."
)


# ============================================================
# Summary metrics
# ============================================================

col1, col2, col3, col4 = st.columns(4)


# ------------------------------------------------------------
# Matches + Most Frequent Shooter Name
# ------------------------------------------------------------

with col1:

    if not filtered_df.empty:

        # Find the most frequent name in the filtered data.
        #
        # value_counts() counts how many rows each shooter name
        # appears in. idxmax() returns the name with the highest
        # frequency.

        name_counts = (
            filtered_df["Name"]
            .value_counts()
        )

        most_frequent_name = name_counts.idxmax()

        match_count = len(filtered_df)

        st.metric(
            "Matches",
            match_count,
            help=f"Most frequent shooter: {most_frequent_name}",
        )

        st.caption(
            f"👤 {most_frequent_name}"
        )

    else:

        st.metric(
            "Matches",
            0,
        )

        st.caption(
            "👤 N/A"
        )


# ------------------------------------------------------------
# Average
# ------------------------------------------------------------

with col2:

    if not filtered_df.empty:

        average_percent = filtered_df["%"].mean()

        st.metric(
            "Average %",
            f"{average_percent:.0f}%",
        )

    else:

        st.metric(
            "Average %",
            "N/A",
        )


# ------------------------------------------------------------
# Best
# ------------------------------------------------------------

with col3:

    if not filtered_df.empty:

        best_percent = filtered_df["%"].max()

        st.metric(
            "Best %",
            f"{best_percent:.0f}%",
        )

    else:

        st.metric(
            "Best %",
            "N/A",
        )


# ------------------------------------------------------------
# Divisions
# ------------------------------------------------------------

with col4:

    st.metric(
        "Divisions",
        filtered_df["Div"].nunique(),
    )


# ============================================================
# Performance chart
# ============================================================

st.subheader("📈 Performance by Division")


if filtered_df.empty:

    st.warning(
        "No match data matches the selected filters."
    )

else:

    # --------------------------------------------------------
    # Create line chart
    # --------------------------------------------------------

    fig = px.line(
        filtered_df,

        x="match_date",

        y="%",

        color="Div",

        markers=True,

        line_shape="linear",

        # Put percentage value on the plot
        text="%",
        
        # Tooltip contains match information,
        # but NOT the percentage.
        hover_data={
            "match_date": "|%Y-%m-%d",
            "%": False,
            "Div": True,
            "match_name": True,
            "Name": True,
        },

        labels={
            "match_date": "Match Date",
            "%": "Performance (%)",
            "Div": "Division",
            "match_name": "Match",
            "Name": "Shooter",
        },
    )


    # --------------------------------------------------------
    # Put rounded integer percentage next to each dot
    # --------------------------------------------------------

    fig.update_traces(
        texttemplate="%{y:.0f}%",
        textposition="top center",
        mode="lines+markers+text",
    )


    # --------------------------------------------------------
    # Chart layout
    # --------------------------------------------------------

    fig.update_layout(

        height=650,

        hovermode="closest",

        legend_title="Division",

        xaxis_title="Match Date",

        yaxis_title="Performance (%)",

        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20,
        ),
    )


    # --------------------------------------------------------
    # Y-axis
    # --------------------------------------------------------

    fig.update_yaxes(
        rangemode="tozero",
    )


    # --------------------------------------------------------
    # Display chart
    # --------------------------------------------------------

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# Division statistics
# ============================================================

st.subheader("📊 Division Statistics")


if not filtered_df.empty:

    stats = (
        filtered_df
        .groupby("Div")["%"]
        .agg(
            Matches="count",
            Average="mean",
            Best="max",
            Worst="min",
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Round to nearest integer
    # --------------------------------------------------------

    stats["Average"] = (
        stats["Average"]
        .round(0)
        .astype(int)
    )

    stats["Best"] = (
        stats["Best"]
        .round(0)
        .astype(int)
    )

    stats["Worst"] = (
        stats["Worst"]
        .round(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # Rename columns
    # --------------------------------------------------------

    stats = stats.rename(
        columns={
            "Div": "Division",
            "Matches": "Matches",
            "Average": "Average %",
            "Best": "Best %",
            "Worst": "Worst %",
        }
    )

    st.dataframe(
        stats,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Detailed match data
# ============================================================

st.subheader("📋 Match Data")


with st.expander("Show detailed match data"):

    display_df = filtered_df.copy()

    # --------------------------------------------------------
    # Format date
    # --------------------------------------------------------

    display_df["match_date"] = (
        display_df["match_date"]
        .dt.strftime("%Y-%m-%d")
    )

    # --------------------------------------------------------
    # Format percentage as integer
    # --------------------------------------------------------

    display_df["%"] = (
        display_df["%"]
        .round(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # Important columns first
    # --------------------------------------------------------

    preferred_columns = [
        "match_date",
        "match_name",
        "Name",
        "Div",
        "%",
    ]

    remaining_columns = [
        col
        for col in display_df.columns
        if col not in preferred_columns
    ]

    display_columns = (
        preferred_columns
        + remaining_columns
    )

    display_df = display_df[
        display_columns
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )