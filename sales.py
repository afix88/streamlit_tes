# import Module 
from re import template
from numpy import nan, select
import pandas as pd
import plotly.express as px
import streamlit as st

#set Layout STREAMLIT
# icon can see in https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon =":bar:chart:",
    layout="wide")

# load dataset
@st.cache_data
def get_data_from_excel():
    df =pd.read_excel('C:\AFIX\'S\Python\Streamlit\Sales Dash\supermarkt_sales.xlsx',
    engine='openpyxl',
    sheet_name='Sales',
    skiprows=3,
    usecols='B:R',
    nrows=1000,
    )
# add column hour 
    df['Hour']=pd.to_datetime(df['Time'],format="%H:%M:%S").dt.hour
    return df
df = get_data_from_excel()



# SIDEBAR 
st.sidebar.header("Please Filter Here:")
city =st.sidebar.multiselect(
    "Select The City :",
    options=df["City"].unique(),
    default=df["City"].unique()
)

st.sidebar.header("Please Filter Here:")
customer =st.sidebar.multiselect(
    "Select The Customer Type :",
    options=df["Customer_type"].unique(),
    default=df["Customer_type"].unique()
)

st.sidebar.header("Please Filter Here:")
gender =st.sidebar.multiselect(
    "Select The Gender :",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

# Selection Filter

df_filter =df.query(
    "City == @city & Customer_type == @customer & Gender == @gender "
)

# MAINPAGE

st.title(":bar_chart: Sales Dashboard")
st.markdown('##')

# TOP KPI
total_sales = int(df_filter['Total'].sum())
average_rating = round(df_filter['Rating'].mean(),1)
start_rating = ":star:" * int(round(df_filter['Rating'].mean(),1)) 
average_total_sales = round(df_filter['Total'].mean(),2)

left_column , middle_column , right_column = st.columns(3)
with left_column : 
    st.subheader("Total Sales :")
    st.subheader(f"US $ {total_sales:,}")
with middle_column :
    st.subheader ("Rating :")
    st.subheader (f"{average_rating}{start_rating}")
with right_column :
    st.subheader("Average Total Sales : ")
    st.subheader(f"US $ {average_total_sales}")


st.markdown("---")


# Sales_by_product_line [ BAR CHART]

sales_by_product_line =(
   df_filter.groupby('Product line',as_index=False).sum()[['Product line','Total']].sort_values('Total')
)
fig_production_sales = px.bar(
    sales_by_product_line , 
    x='Total', 
    y='Product line',
    title="<b> Sales by Product line </b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
    )
fig_production_sales.update_layout( 
    plot_bgcolor = 'rgba(0,0,0,0)',
    xaxis = (dict(showgrid=False)), 
)

# Sales_by_Hour [ BAR CHART]

sales_by_hour = (
    df_filter.groupby('Hour', as_index=False).sum()[['Hour','Total']].sort_values('Hour')
    )
fig_production_hour = px.bar(
    sales_by_hour ,
    x='Hour',
    y='Total',
    title="<b> Sales by Hour </b>",
    color_discrete_sequence=["#0083B8"  ] * len(sales_by_hour),
    template="plotly_white")
fig_production_hour.update_layout( 
    xaxis =dict(tickmode="linear"),
    plot_bgcolor = 'rgba(0,0,0,0)',
    yaxis = (dict(showgrid=False)), 
)


left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_production_hour,use_container_width=True)
right_column.plotly_chart(fig_production_sales,use_container_width=True)

# --- HIDE STREAMLIT STYLE ----- #
hide_st_style = """
                <style>
                #MainMenu {Visibility: hidden;}
                footer {Visibility: hidden;}
                header {Visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)

