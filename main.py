
import pandas as panda  # pip install pandas openpyxl
import plotly.express as plotly  # pip install plotly-express
import streamlit as st  # pip install streamlit

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Manals world", page_icon=":bar_chart:", layout="wide")

# ---- READ EXCEL ----
@st.cache_data
def get_data_from_excel():
    data = panda.read_excel(
        io="supermarkt_sales.xlsx", # file name
        engine="openpyxl", 
        sheet_name="Sales", # excel sheet name
        skiprows=3, # rows to skip
        usecols="B:R",  # columns to use
        nrows=1000, # number of rows
    )
    # Add 'hour' column to dataframe
    data["hour"] = panda.to_datetime(data["Time"], format="%H:%M:%S").dt.hour
    return data

data = get_data_from_excel()

# ---- SIDEBAR ----
# City multiselect
st.sidebar.header("Please Select Filter:")
city = st.sidebar.multiselect(
    "Select the City:",
    options=data["City"].unique(),
    default=data["City"].unique()
)

# customer multiselect
customer_type = st.sidebar.multiselect(
    "Select the Customer Type:",
    options=data["Customer_type"].unique(),
    default=data["Customer_type"].unique(),
)
# gender multiselect
gender = st.sidebar.multiselect(
    "Select the Gender:",
    options=data["Gender"].unique(),
    default=data["Gender"].unique()
)

data_selection = data.query(
    "City == @city & Customer_type ==@customer_type & Gender == @gender"
)

# Check if the dataframe is empty:
if data_selection.empty:
    st.warning("No data is available based on the current filter settings!")
    st.stop() # This will halt the app from further execution.

# ---- MAINPAGE ----
st.title("Manal's Dashboard")
st.markdown("##")

# TOP KPI's
total_sales = int(data_selection["Total"].sum())
average_rating = round(data_selection["Rating"].mean(), 1)
star_rating = ":star:" * int(round(average_rating, 0))
average_sale_by_transaction = round(data_selection["Total"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"US $ {total_sales:,}")
with middle_column:
    st.subheader("Average Rating:")
    st.subheader(f"{average_rating} {star_rating}")
with right_column:
    st.subheader("Average Sales Per Transaction:")
    st.subheader(f"US $ {average_sale_by_transaction}")

st.markdown("""---""")

# SALES BY PRODUCT LINE [BAR CHART]
sales_by_product_line = data_selection.groupby(by=["Product line"])[["Total"]].sum().sort_values(by="Total")
fig_product_sales = plotly.bar(
    sales_by_product_line,
    x="Total",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Sales by Product Line</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# SALES BY HOUR [BAR CHART]
sales_by_hour = data_selection.groupby(by=["hour"])[["Total"]].sum()
fig_hourly_sales = plotly.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Total",
    title="<b>Sales by hour</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
    template="plotly_white",
)
fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)


left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
