import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Diwali Sales Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Diwali Sales Analysis Dashboard")

# Load data
df = pd.read_csv("Diwali Sales Data.csv", encoding="unicode_escape")

# Data Cleaning
df.drop(columns=["Status", "unnamed1"], inplace=True, errors="ignore")
df.dropna(inplace=True)

if "Amount" in df.columns:
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

# Sidebar Filters
st.sidebar.header("Filters")

states = st.sidebar.multiselect(
    "Select State",
    options=sorted(df["State"].unique()),
    default=sorted(df["State"].unique())
)

gender = st.sidebar.multiselect(
    "Select Gender",
    options=sorted(df["Gender"].unique()),
    default=sorted(df["Gender"].unique())
)

filtered_df = df[
    (df["State"].isin(states)) &
    (df["Gender"].isin(gender))
]

# KPIs
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Sales", f"₹{filtered_df['Amount'].sum():,.0f}")

with col2:
    st.metric("Orders", len(filtered_df))

with col3:
    st.metric("Average Sales", f"₹{filtered_df['Amount'].mean():,.0f}")

st.divider()

# Sales by Gender
st.subheader("Sales by Gender")

gender_sales = (
    filtered_df.groupby("Gender")["Amount"]
    .sum()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(6,4))
gender_sales.plot(kind="bar", ax=ax)
st.pyplot(fig)

# Top States
st.subheader("Top 10 States by Sales")

state_sales = (
    filtered_df.groupby("State")["Amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(x=state_sales.values, y=state_sales.index, ax=ax)
st.pyplot(fig)

# Occupation Analysis
st.subheader("Sales by Occupation")

occupation_sales = (
    filtered_df.groupby("Occupation")["Amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(x=occupation_sales.values, y=occupation_sales.index, ax=ax)
st.pyplot(fig)

st.subheader("Dataset Preview")
st.dataframe(filtered_df.head(100))