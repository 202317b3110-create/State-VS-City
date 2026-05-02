import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Data Compare Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a cleaner, modern look (Fixed for Dark Mode visibility)
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* Modern Metric Box Styling */
    div[data-testid="metric-container"] {
        background-color: #262730; /* Dark card background */
        border: 1px solid #334155; /* Subtle border */
        padding: 15px; 
        border-radius: 8px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Force text colors to be visible in the metric boxes */
    div[data-testid="metric-container"] label {
        color: #94A3B8 !important; /* Light gray for the title/label */
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        color: #F8FAFC !important; /* Bright white for the actual number */
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DYNAMIC FILE UPLOADERS (Ready for Cloud Deployment)
# -----------------------------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=50) # Optional logo
st.sidebar.title("Dashboard Controls")

st.sidebar.header("📂 Upload Datasets")
uploaded_file_1 = st.sidebar.file_uploader("Upload Dataset A (CSV)", type=["csv"], key="file1")
uploaded_file_2 = st.sidebar.file_uploader("Upload Dataset B (CSV)", type=["csv"], key="file2")

# -----------------------------------------------------------------------------
# DATA LOADING FUNCTION
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(uploaded_file, dataset_name):
    """Loads CSV data dynamically. Generates mock data if no file is uploaded."""
    if uploaded_file is not None:
        # Read the uploaded file directly
        df = pd.read_csv(uploaded_file)
        return df
    else:
        # Generate mock data so the dashboard still renders while waiting for an upload
        np.random.seed(42 if dataset_name == "Dataset A" else 99)
        categories = ['Electronics', 'Clothing', 'Home', 'Beauty', 'Sports']
        regions = ['North', 'South', 'East', 'West']
        data = {
            'Category': np.random.choice(categories, 200),
            'Region': np.random.choice(regions, 200),
            'Revenue': np.random.uniform(100, 5000, 200).round(2),
            'Units_Sold': np.random.randint(1, 100, 200),
            'Date': pd.date_range(start='2023-01-01', periods=200)
        }
        return pd.DataFrame(data)

# Load the datasets
df1 = load_data(uploaded_file_1, "Dataset A")
df2 = load_data(uploaded_file_2, "Dataset B")

# -----------------------------------------------------------------------------
# SIDEBAR: FILTERS
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("Filter your data views below.")

# Dynamic categorical filter
common_columns = list(set(df1.columns) & set(df2.columns))

if 'Category' in common_columns:
    all_categories = sorted(list(set(df1['Category'].unique()) | set(df2['Category'].unique())))
    selected_categories = st.sidebar.multiselect(
        "Select Categories",
        options=all_categories,
        default=all_categories
    )
    
    # Apply filters
    if selected_categories:
        df1 = df1[df1['Category'].isin(selected_categories)]
        df2 = df2[df2['Category'].isin(selected_categories)]

# -----------------------------------------------------------------------------
# MAIN DASHBOARD
# -----------------------------------------------------------------------------
st.title("📊 Dataset Comparison Dashboard")
st.markdown("Compare key metrics, distributions, and trends across two distinct datasets side-by-side.")
st.markdown("---")

# Layout: Two main columns for side-by-side comparison
col1, col2 = st.columns(2)

# ==========================================
# DATASET 1 VIEW
# ==========================================
with col1:
    st.header("Dataset A")
    # Dynamically update the source name based on the uploaded file
    if uploaded_file_1:
        st.caption(f"Source: `{uploaded_file_1.name}`")
    else:
        st.caption("Source: `Sample Data`")
    
    # 1. KPIs / Metrics
    kpi1_a, kpi2_a = st.columns(2)
    with kpi1_a:
        st.metric(label="Total Records", value=f"{len(df1):,}")
    with kpi2_a:
        if 'Revenue' in df1.columns:
            st.metric(label="Total Revenue", value=f"${df1['Revenue'].sum():,.2f}")
        else:
            st.metric(label="Total Columns", value=len(df1.columns))
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Modern Graph: Bar Chart
    if 'Category' in df1.columns and 'Revenue' in df1.columns:
        fig_bar1 = px.bar(
            df1.groupby('Category')['Revenue'].sum().reset_index(),
            x='Category', y='Revenue',
            title="Revenue by Category",
            color='Category',
            template="plotly_dark", # Switched to plotly_dark to match Streamlit dark mode
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar1.update_layout(showlegend=False, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_bar1, width="stretch")

    # 3. Pie Chart
    if 'Region' in df1.columns:
        fig_pie1 = px.pie(
            df1, names='Region',
            title="Distribution by Region",
            hole=0.4,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_pie1.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_pie1, use_container_width=True)

# ==========================================
# DATASET 2 VIEW
# ==========================================
with col2:
    st.header("Dataset B")
    if uploaded_file_2:
        st.caption(f"Source: `{uploaded_file_2.name}`")
    else:
        st.caption("Source: `Sample Data`")
    
    # 1. KPIs / Metrics
    kpi1_b, kpi2_b = st.columns(2)
    with kpi1_b:
        st.metric(label="Total Records", value=f"{len(df2):,}")
    with kpi2_b:
        if 'Revenue' in df2.columns:
            st.metric(label="Total Revenue", value=f"${df2['Revenue'].sum():,.2f}")
        else:
            st.metric(label="Total Columns", value=len(df2.columns))
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Modern Graph: Bar Chart
    if 'Category' in df2.columns and 'Revenue' in df2.columns:
        fig_bar2 = px.bar(
            df2.groupby('Category')['Revenue'].sum().reset_index(),
            x='Category', y='Revenue',
            title="Revenue by Category",
            color='Category',
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar2.update_layout(showlegend=False, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_bar2, use_container_width=True)

    # 3. Pie Chart
    if 'Region' in df2.columns:
        fig_pie2 = px.pie(
            df2, names='Region',
            title="Distribution by Region",
            hole=0.4,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Burg
        )
        fig_pie2.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_pie2, use_container_width=True)

# -----------------------------------------------------------------------------
# COMBINED DATA VIEW
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("Raw Data Preview")

tab1, tab2 = st.tabs(["Dataset A Preview", "Dataset B Preview"])
with tab1:
    st.dataframe(df1.head(10), use_container_width=True)
with tab2:
    st.dataframe(df2.head(10), use_container_width=True)