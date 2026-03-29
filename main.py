import pandas as pd
import streamlit as st
import plotly.express as px

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Language Usage Dashboard", layout="wide")

st.title("Programming Language Usage Dashboard")


# ---- LOAD DATA ----
@st.cache_data
def load_data():
    df = pd.read_excel("stackoverflow-2023.xlsx")  # change to your file name

    # Clean column names (avoids KeyError issues)
    df.columns = df.columns.str.strip()

    return df


df = load_data()

# ---- CLEAN + TRANSFORM DATA ----
# Split and expand languages
df = df.assign(
    LanguageHaveWorkedWith=df["LanguageHaveWorkedWith"].str.split(";")
).explode("LanguageHaveWorkedWith")

# ---- CALCULATE PERCENTAGES ----
# Count unique users per language
language_counts = df.groupby("LanguageHaveWorkedWith")["ResponseId"].nunique()

# Total users
total_users = df["ResponseId"].nunique()

# Percentage
language_percentages = (language_counts / total_users) * 100

# Convert to DataFrame for plotting
language_df = language_percentages.reset_index()
language_df.columns = ["Language", "Percentage"]

# ---- PIE CHART ----
fig = px.pie(
    language_df,
    names="Language",
    values="Percentage",
    title="Percentage of Programming Languages Used"
)

st.plotly_chart(fig, use_container_width=True)


# ---- FUNCTION: LINE CHART FOR ANY LANGUAGE ----
def plot_language_trend(language_name):
    df_years = df.copy()

    # Clean YearsCode
    df_years["YearsCode"] = df_years["YearsCode"].replace({
        "Less than 1 year": 0,
        "More than 50 years": 50
    })
    df_years["YearsCode"] = pd.to_numeric(df_years["YearsCode"], errors="coerce")
    df_years = df_years.dropna(subset=["YearsCode"])

    # Total users per YearsCode
    total_by_year = df_years.groupby("YearsCode")["ResponseId"].nunique()

    # Users of selected language
    lang_users = df_years[df_years["LanguageHaveWorkedWith"] == language_name] \
        .groupby("YearsCode")["ResponseId"].nunique()

    # Percentage
    lang_percentage = (lang_users / total_by_year) * 100

    # Convert to DataFrame
    trend_df = lang_percentage.reset_index()
    trend_df.columns = ["YearsCode", "Percentage"]
    trend_df = trend_df.sort_values("YearsCode")

    # Plot
    fig = px.line(
        trend_df,
        x="YearsCode",
        y="Percentage",
        title=f"{language_name} Usage (%) vs Years of Coding Experience",
        markers=True
    )

    return fig


# ---- CREATE TABS ----
st.markdown("---")
st.subheader("Language Trends by Experience")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "JavaScript", "HTML/CSS", "SQL", "Python", "Java"
])

with tab1:
    st.plotly_chart(plot_language_trend("JavaScript"), use_container_width=True)

with tab2:
    st.plotly_chart(plot_language_trend("HTML/CSS"), use_container_width=True)

with tab3:
    st.plotly_chart(plot_language_trend("SQL"), use_container_width=True)

with tab4:
    st.plotly_chart(plot_language_trend("Python"), use_container_width=True)

with tab5:
    st.plotly_chart(plot_language_trend("Java"), use_container_width=True)


# ---- FUNCTION: LANGUAGE % BY DEV TYPE ----
def plot_devtype_trend(language_name):
    df_dev = df.copy()

    # Remove missing DevType
    df_dev = df_dev.dropna(subset=["DevType"])

    # Split DevType (since it can also have multiple roles)
    df_dev = df_dev.assign(
        DevType=df_dev["DevType"].str.split(";")
    ).explode("DevType")

    # Total users per DevType
    total_by_dev = df_dev.groupby("DevType")["ResponseId"].nunique()

    # Users of selected language per DevType
    lang_users = df_dev[df_dev["LanguageHaveWorkedWith"] == language_name] \
        .groupby("DevType")["ResponseId"].nunique()

    # Percentage
    lang_percentage = (lang_users / total_by_dev) * 100

    # Convert to DataFrame
    dev_df = lang_percentage.reset_index()
    dev_df.columns = ["DevType", "Percentage"]

    # Sort for readability
    dev_df = dev_df.sort_values("Percentage", ascending=False)

    # Plot (horizontal bar works better than line here)
    fig = px.bar(
        dev_df,
        x="Percentage",
        y="DevType",
        orientation="h",
        title=f"{language_name} Usage (%) by Developer Type"
    )

    return fig


# ---- NEW SECTION ----
st.markdown("---")
st.subheader("Language Usage by Developer Type")

# Tabs for languages
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "JavaScript", "HTML/CSS", "SQL", "Python", "Java"
])

with tab1:
    st.plotly_chart(plot_devtype_trend("JavaScript"), use_container_width=True)

with tab2:
    st.plotly_chart(plot_devtype_trend("HTML/CSS"), use_container_width=True)

with tab3:
    st.plotly_chart(plot_devtype_trend("SQL"), use_container_width=True)

with tab4:
    st.plotly_chart(plot_devtype_trend("Python"), use_container_width=True)

with tab5:
    st.plotly_chart(plot_devtype_trend("Java"), use_container_width=True)