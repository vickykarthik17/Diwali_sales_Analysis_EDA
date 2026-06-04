import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Diwali Sales Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Disable deprecation warnings
st.set_option('deprecation.showPyplotGlobalUse', False)

# Custom styling
st.markdown("""
    <style>
    .metric-container { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
    .section-header { color: #ff6b35; font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Diwali Sales Analysis Dashboard")
st.markdown("*Advanced Analytics & Customer Insights*")

# Load data with caching
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Diwali Sales Data.csv", encoding="unicode_escape")
        df.drop(columns=["Status", "unnamed1"], inplace=True, errors="ignore")
        df.dropna(inplace=True)
        if "Amount" in df.columns:
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

@st.cache_data
def get_filter_options(df):
    """Cache filter options to avoid recalculation"""
    return {
        'states': sorted(df["State"].unique()),
        'genders': sorted(df["Gender"].unique()),
        'age_groups': sorted(df["Age Group"].unique()),
        'occupations': sorted(df["Occupation"].unique()),
        'categories': sorted(df["Product_Category"].unique()),
        'marital': sorted(df["Marital_Status"].unique())
    }

@st.cache_data
def precompute_aggregations(df):
    """Pre-compute heavy aggregations"""
    return {
        'gender_sales': df.groupby("Gender")["Amount"].sum().sort_values(ascending=False),
        'state_sales': df.groupby("State")["Amount"].sum().sort_values(ascending=False),
        'occupation_sales': df.groupby("Occupation")["Amount"].sum().sort_values(ascending=False),
        'category_sales': df.groupby("Product_Category")["Amount"].sum().sort_values(ascending=False),
        'zone_sales': df.groupby("Zone")["Amount"].sum(),
        'age_sales': df.groupby("Age Group")["Amount"].sum(),
        'marital_sales': df.groupby("Marital_Status")["Amount"].sum()
    }

df = load_data()

if df is None:
    st.stop()

filter_opts = get_filter_options(df)
agg_data = precompute_aggregations(df)

# ============ SIDEBAR FILTERS ============
st.sidebar.header("🔍 Filters")

states = st.sidebar.multiselect(
    "Select States",
    options=filter_opts['states'],
    default=filter_opts['states'][:5],
    help="Filter data by states"
)

gender = st.sidebar.multiselect(
    "Select Gender",
    options=filter_opts['genders'],
    default=filter_opts['genders'],
    help="Filter by customer gender"
)

age_groups = st.sidebar.multiselect(
    "Select Age Groups",
    options=filter_opts['age_groups'],
    default=filter_opts['age_groups'],
    help="Filter by age demographics"
)

occupations = st.sidebar.multiselect(
    "Select Occupations",
    options=filter_opts['occupations'],
    default=filter_opts['occupations'][:10],
    help="Filter by occupation"
)

product_categories = st.sidebar.multiselect(
    "Select Product Categories",
    options=filter_opts['categories'],
    default=filter_opts['categories'],
    help="Filter by product type"
)

marital_status = st.sidebar.multiselect(
    "Select Marital Status",
    options=filter_opts['marital'],
    default=filter_opts['marital'],
    help="Filter by marital status"
)

# Apply all filters
filtered_df = df[
    (df["State"].isin(states)) &
    (df["Gender"].isin(gender)) &
    (df["Age Group"].isin(age_groups)) &
    (df["Occupation"].isin(occupations)) &
    (df["Product_Category"].isin(product_categories)) &
    (df["Marital_Status"].isin(marital_status))
]

# ============ KEY METRICS ============
st.markdown("---")
st.markdown("### 📈 Key Performance Indicators")

col1, col2, col3, col4, col5, col6 = st.columns(6)

total_sales = filtered_df['Amount'].sum()
total_orders = len(filtered_df)
avg_order_value = filtered_df['Amount'].mean()
unique_customers = filtered_df['User_ID'].nunique()
avg_quantity = filtered_df['Orders'].mean()
top_product = filtered_df['Product_Category'].value_counts().index[0] if len(filtered_df) > 0 else "N/A"

with col1:
    st.metric("💰 Total Sales", f"₹{total_sales:,.0f}")

with col2:
    st.metric("📦 Total Orders", f"{total_orders:,}")

with col3:
    st.metric("💵 Avg Order", f"₹{avg_order_value:,.0f}")

with col4:
    st.metric("👥 Customers", f"{unique_customers:,}")

with col5:
    st.metric("📊 Qty", f"{avg_quantity:.1f}")

with col6:
    st.metric("🏆 Top", top_product[:8])

st.markdown("---")

# ============ TABS FOR ORGANIZATION ============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Sales Overview", 
    "👥 Customer Analysis", 
    "🛍️ Product Insights", 
    "📍 Geo Analysis",
    "📋 Data View"
])

# ============ TAB 1: SALES OVERVIEW ============
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        gender_sales = filtered_df.groupby("Gender")["Amount"].sum().sort_values(ascending=False)
        fig = px.bar(
            x=gender_sales.values,
            y=gender_sales.index,
            orientation='h',
            title="Gender-wise Sales",
            labels={'x': 'Sales Amount (₹)', 'y': 'Gender'},
            color=gender_sales.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        gender_pct = (filtered_df.groupby("Gender")["Amount"].sum() / filtered_df["Amount"].sum() * 100)
        fig = px.pie(
            values=gender_pct.values,
            names=gender_pct.index,
            title="Sales % by Gender"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        marital_sales = filtered_df.groupby("Marital_Status")["Amount"].sum().sort_values(ascending=False)
        fig = px.bar(
            x=marital_sales.values,
            y=marital_sales.index,
            orientation='h',
            title="Sales by Marital Status",
            labels={'x': 'Sales Amount (₹)', 'y': 'Status'}
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        marital_count = filtered_df.groupby("Marital_Status").size()
        fig = px.bar(
            x=marital_count.index,
            y=marital_count.values,
            title="Orders by Marital Status",
            labels={'x': 'Status', 'y': 'Count'}
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ============ TAB 2: CUSTOMER ANALYSIS ============
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        age_sales = filtered_df.groupby("Age Group")["Amount"].sum().sort_values(ascending=False)
        fig = px.bar(
            x=age_sales.index,
            y=age_sales.values,
            title="Sales by Age Group",
            labels={'x': 'Age Group', 'y': 'Sales (₹)'},
            color=age_sales.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=300, showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        age_count = filtered_df.groupby("Age Group").size()
        fig = px.bar(
            x=age_count.index,
            y=age_count.values,
            title="Customer Count by Age",
            labels={'x': 'Age Group', 'y': 'Count'}
        )
        fig.update_layout(height=300, showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Customer Segmentation")
    col1, col2, col3, col4 = st.columns(4)
    
    q1, q3 = filtered_df['Amount'].quantile([0.25, 0.75])
    high_val = len(filtered_df[filtered_df['Amount'] > q3])
    med_val = len(filtered_df[(filtered_df['Amount'] <= q3) & (filtered_df['Amount'] > q1)])
    low_val = len(filtered_df[filtered_df['Amount'] <= q1])
    
    with col1:
        st.metric("High-Value", f"{high_val:,}")
    with col2:
        st.metric("Medium-Value", f"{med_val:,}")
    with col3:
        st.metric("Low-Value", f"{low_val:,}")
    with col4:
        st.metric("Repeat Customers", f"{len(filtered_df[filtered_df['Orders'] > 1]):,}")

# ============ TAB 3: PRODUCT INSIGHTS ============
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        top_products = filtered_df.groupby("Product_Category")["Amount"].sum().sort_values(ascending=False).head(10)
        fig = px.bar(
            x=top_products.values,
            y=top_products.index,
            orientation='h',
            title="Top 10 Product Categories",
            labels={'x': 'Sales (₹)', 'y': ''},
            color=top_products.values,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        product_count = filtered_df['Product_Category'].value_counts().head(10)
        fig = px.bar(
            x=product_count.values,
            y=product_count.index,
            orientation='h',
            title="Most Ordered Categories",
            labels={'x': 'Count', 'y': ''}
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Product Stats (Top 15)")
    product_stats = filtered_df.groupby("Product_Category").agg({
        "Amount": ["sum", "mean", "count"]
    }).round(0)
    product_stats.columns = ["Total", "Avg", "Orders"]
    product_stats = product_stats.sort_values("Total", ascending=False).head(15)
    st.dataframe(product_stats, use_container_width=True)

# ============ TAB 4: GEO ANALYSIS ============
with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        state_sales = filtered_df.groupby("State")["Amount"].sum().sort_values(ascending=False).head(15)
        fig = px.bar(
            x=state_sales.values,
            y=state_sales.index,
            orientation='h',
            title="Top 15 States by Sales",
            labels={'x': 'Sales (₹)', 'y': ''},
            color=state_sales.values,
            color_continuous_scale='Mako'
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        state_count = filtered_df['State'].value_counts().head(15)
        fig = px.bar(
            x=state_count.values,
            y=state_count.index,
            orientation='h',
            title="Top 15 States by Orders",
            labels={'x': 'Count', 'y': ''}
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Zone Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        zone_sales = filtered_df.groupby("Zone")["Amount"].sum().sort_values(ascending=False)
        fig = px.bar(
            x=zone_sales.index,
            y=zone_sales.values,
            title="Sales by Zone",
            labels={'x': 'Zone', 'y': 'Sales (₹)'}
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        zone_count = filtered_df['Zone'].value_counts()
        fig = px.pie(
            values=zone_count.values,
            names=zone_count.index,
            title="Zone Distribution %"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        col_a, col_b = st.columns(1)
        st.metric("States", len(filtered_df["State"].unique()))
        st.metric("Zones", len(filtered_df["Zone"].unique()))
        st.metric("Avg/State", f"₹{filtered_df.groupby('State')['Amount'].sum().mean():,.0f}")

# ============ TAB 5: DATA VIEW ============
with tab5:
    st.subheader("Filtered Dataset")
    st.info(f"📊 {len(filtered_df):,} records | {len(df):,} total")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "diwali_sales.csv", "text/csv")
    with col2:
        st.metric("Records", len(filtered_df))
    with col3:
        st.metric("Columns", len(filtered_df.columns))
    
    rows = st.slider("Rows:", 10, 500, 50)
    st.dataframe(filtered_df.head(rows), use_container_width=True, height=400)

st.markdown("---")
st.markdown("⚡ *Optimized Dashboard - v3.0*")

with col6:
    top_product = filtered_df['Product_Category'].value_counts().index[0] if len(filtered_df) > 0 else "N/A"
    st.metric("🏆 Top Category", top_product)

st.markdown("---")

# ============ TABS FOR ORGANIZATION ============
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Sales Overview", 
    "👥 Customer Analysis", 
    "🛍️ Product Insights", 
    "📍 Geo Analysis",
    "💡 Advanced Analytics",
    "📋 Data View"
])

# ============ TAB 1: SALES OVERVIEW ============
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales by Gender")
        gender_sales = filtered_df.groupby("Gender")["Amount"].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = sns.color_palette("husl", len(gender_sales))
        gender_sales.plot(kind="bar", ax=ax, color=colors)
        ax.set_title("Gender-wise Sales Distribution", fontsize=14, fontweight='bold')
        ax.set_ylabel("Sales Amount (₹)")
        ax.set_xlabel("Gender")
        plt.xticks(rotation=0)
        st.pyplot(fig)
    
    with col2:
        st.subheader("Sales Distribution by Gender (%)")
        gender_pct = (filtered_df.groupby("Gender")["Amount"].sum() / filtered_df["Amount"].sum() * 100)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.pie(gender_pct, labels=gender_pct.index, autopct='%1.1f%%', startangle=90)
        ax.set_title("Gender Sales Percentage", fontsize=14, fontweight='bold')
        st.pyplot(fig)
    
    # Sales by Marital Status
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sales by Marital Status")
        marital_sales = filtered_df.groupby("Marital_Status")["Amount"].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=marital_sales.values, y=marital_sales.index, ax=ax, palette="Set2")
        ax.set_title("Marital Status Impact on Sales", fontsize=14, fontweight='bold')
        ax.set_xlabel("Sales Amount (₹)")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Order Count by Marital Status")
        marital_count = filtered_df.groupby("Marital_Status").size().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(marital_count.index, marital_count.values, color=sns.color_palette("coolwarm", len(marital_count)))
        ax.set_title("Customer Count by Marital Status", fontsize=14, fontweight='bold')
        ax.set_xlabel("Number of Orders")
        st.pyplot(fig)

# ============ TAB 2: CUSTOMER ANALYSIS ============
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales by Age Group")
        age_sales = filtered_df.groupby("Age Group")["Amount"].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=age_sales.values, y=age_sales.index, ax=ax, palette="viridis")
        ax.set_title("Age Group Sales Performance", fontsize=14, fontweight='bold')
        ax.set_xlabel("Sales Amount (₹)")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Customer Count by Age Group")
        age_count = filtered_df.groupby("Age Group").size()
        fig, ax = plt.subplots(figsize=(10, 5))
        age_count.plot(kind="bar", ax=ax, color=sns.color_palette("Set1", len(age_count)))
        ax.set_title("Customers Distribution by Age", fontsize=14, fontweight='bold')
        ax.set_ylabel("Number of Customers")
        ax.set_xlabel("Age Group")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    # Customer Segmentation
    st.subheader("Customer Segmentation Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("High-Value Customers", f"{len(filtered_df[filtered_df['Amount'] > filtered_df['Amount'].quantile(0.75)])}")
        st.metric("Medium-Value Customers", f"{len(filtered_df[(filtered_df['Amount'] <= filtered_df['Amount'].quantile(0.75)) & (filtered_df['Amount'] > filtered_df['Amount'].quantile(0.25))])}")
    
    with col2:
        st.metric("Low-Value Customers", f"{len(filtered_df[filtered_df['Amount'] <= filtered_df['Amount'].quantile(0.25)])}")
        st.metric("Repeat Customers (Orders>1)", f"{len(filtered_df[filtered_df['Orders'] > 1])}")

# ============ TAB 3: PRODUCT INSIGHTS ============
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Product Categories by Sales")
        product_sales = filtered_df.groupby("Product_Category")["Amount"].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=product_sales.values, y=product_sales.index, ax=ax, palette="RdYlGn")
        ax.set_title("Top Product Categories", fontsize=14, fontweight='bold')
        ax.set_xlabel("Sales Amount (₹)")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Top 10 Products by Order Count")
        product_count = filtered_df['Product_Category'].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        product_count.plot(kind="barh", ax=ax, color=sns.color_palette("twilight", len(product_count)))
        ax.set_title("Most Ordered Product Categories", fontsize=14, fontweight='bold')
        ax.set_xlabel("Number of Orders")
        st.pyplot(fig)
    
    # Product stats
    st.subheader("Product Category Statistics")
    product_stats = filtered_df.groupby("Product_Category").agg({
        "Amount": ["sum", "mean", "count"]
    }).round(2)
    product_stats.columns = ["Total Sales", "Avg Sales", "Order Count"]
    product_stats = product_stats.sort_values("Total Sales", ascending=False).head(15)
    st.dataframe(product_stats, use_container_width=True)

# ============ TAB 4: GEO ANALYSIS ============
with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 15 States by Sales")
        state_sales = filtered_df.groupby("State")["Amount"].sum().sort_values(ascending=False).head(15)
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.barplot(x=state_sales.values, y=state_sales.index, ax=ax, palette="mako")
        ax.set_title("Top States by Revenue", fontsize=14, fontweight='bold')
        ax.set_xlabel("Sales Amount (₹)")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Top 15 States by Order Count")
        state_count = filtered_df['State'].value_counts().head(15)
        fig, ax = plt.subplots(figsize=(10, 8))
        state_count.plot(kind="barh", ax=ax, color=sns.color_palette("husl", len(state_count)))
        ax.set_title("Top States by Orders", fontsize=14, fontweight='bold')
        ax.set_xlabel("Number of Orders")
        st.pyplot(fig)
    
    st.subheader("Zone-wise Performance")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        zone_sales = filtered_df.groupby("Zone")["Amount"].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8, 5))
        zone_sales.plot(kind="bar", ax=ax, color=sns.color_palette("Spectral", len(zone_sales)))
        ax.set_title("Zone-wise Sales", fontsize=12, fontweight='bold')
        ax.set_ylabel("Sales Amount (₹)")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    with col2:
        zone_count = filtered_df['Zone'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.pie(zone_count, labels=zone_count.index, autopct='%1.1f%%', startangle=90)
        ax.set_title("Zone Distribution (%)", fontsize=12, fontweight='bold')
        st.pyplot(fig)
    
    with col3:
        st.metric("Number of States", len(filtered_df["State"].unique()))
        st.metric("Number of Zones", len(filtered_df["Zone"].unique()))
        st.metric("Average per State", f"₹{filtered_df.groupby('State')['Amount'].sum().mean():,.0f}")

# ============ TAB 5: ADVANCED ANALYTICS ============
with tab5:
    st.subheader("Occupation-wise Performance")
    occupation_data = filtered_df.groupby("Occupation").agg({
        "Amount": ["sum", "mean", "count"]
    }).round(2)
    occupation_data.columns = ["Total Sales", "Avg Sales", "Order Count"]
    occupation_data = occupation_data.sort_values("Total Sales", ascending=False)
    
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        occupation_data["Total Sales"].plot(kind="barh", ax=ax, color=sns.color_palette("coolwarm", len(occupation_data)))
        ax.set_title("Sales by Occupation", fontsize=14, fontweight='bold')
        ax.set_xlabel("Sales Amount (₹)")
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots(figsize=(10, 6))
        occupation_data["Order Count"].plot(kind="barh", ax=ax, color=sns.color_palette("YlOrRd", len(occupation_data)))
        ax.set_title("Order Count by Occupation", fontsize=14, fontweight='bold')
        ax.set_xlabel("Number of Orders")
        st.pyplot(fig)
    
    st.dataframe(occupation_data, use_container_width=True)
    
    # Summary Statistics
    st.subheader("Statistical Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Mean Sales", f"₹{filtered_df['Amount'].mean():,.0f}")
    with col2:
        st.metric("Median Sales", f"₹{filtered_df['Amount'].median():,.0f}")
    with col3:
        st.metric("Std Deviation", f"₹{filtered_df['Amount'].std():,.0f}")
    with col4:
        st.metric("Sales Range", f"₹{filtered_df['Amount'].max() - filtered_df['Amount'].min():,.0f}")
    
    # Heatmap: Gender vs Age Group
    st.subheader("Sales Heatmap: Gender vs Age Group")
    heatmap_data = filtered_df.pivot_table(
        values="Amount", 
        index="Age Group", 
        columns="Gender", 
        aggfunc="sum"
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax, cbar_kws={'label': 'Sales Amount (₹)'})
    ax.set_title("Sales Heatmap: Gender vs Age Group", fontsize=14, fontweight='bold')
    st.pyplot(fig)

# ============ TAB 6: DATA VIEW ============
with tab6:
    st.subheader("Filtered Dataset")
    st.info(f"Showing {len(filtered_df)} records out of {len(df)} total records")
    
    # Data export options
    col1, col2, col3 = st.columns(3)
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="diwali_sales_filtered.csv",
            mime="text/csv"
        )
    
    with col2:
        st.metric("Records Displayed", len(filtered_df))
    
    with col3:
        st.metric("Columns", len(filtered_df.columns))
    
    # Display dataframe with pagination
    rows_to_show = st.slider("Rows to display:", 10, 500, 50)
    st.dataframe(filtered_df.head(rows_to_show), use_container_width=True)
    
    # Column-wise statistics
    st.subheader("Column Statistics")
    st.dataframe(filtered_df.describe().round(2), use_container_width=True)

st.markdown("---")
st.markdown("📊 *Dashboard Last Updated: Diwali Sales Analysis v2.0*")