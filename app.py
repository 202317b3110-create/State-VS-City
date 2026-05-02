import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & CSS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Real Estate Insights Pro", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    div[data-testid="metric-container"] {
        background-color: #262730; border: 1px solid #334155; padding: 15px; 
        border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] label { color: #94A3B8 !important; font-weight: 600; }
    div[data-testid="stMetricValue"] { color: #F8FAFC !important; }
    hr { margin-top: 1rem; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def find_default_col(columns, keywords):
    """Tries to auto-detect columns based on common real estate keywords."""
    for col in columns:
        if any(keyword.lower() in col.lower() for keyword in keywords):
            return col
    return "Not Selected"

@st.cache_data
def load_data(uploaded_file, dataset_name):
    """Loads CSV or generates Real Estate Mock Data if empty."""
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    else:
        # Generate REAL ESTATE mock data
        np.random.seed(42 if dataset_name == "A" else 99)
        locations = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Pune']
        types = ['Apartment', 'Villa', 'Independent House', 'Studio']
        data = {
            'City_Name': np.random.choice(locations, 200),
            'Property_Type': np.random.choice(types, 200),
            'Sale_Price': np.random.uniform(2000000, 15000000, 200),
            'Build_Up_Area_SqFt': np.random.uniform(500, 4000, 200),
            'Rental_Yield_Pct': np.random.uniform(2, 8, 200),
            'Attraction_Score': np.random.uniform(1, 10, 200).round(1)
        }
        return pd.DataFrame(data)

# -----------------------------------------------------------------------------
# SIDEBAR: UPLOADS
# -----------------------------------------------------------------------------
st.sidebar.title("🏢 Real Estate Compare")
st.sidebar.header("📂 Upload Datasets")
uploaded_file_1 = st.sidebar.file_uploader("Upload Dataset A (CSV)", type=["csv"])
uploaded_file_2 = st.sidebar.file_uploader("Upload Dataset B (CSV)", type=["csv"])

df1 = load_data(uploaded_file_1, "A")
df2 = load_data(uploaded_file_2, "B")

source_1 = uploaded_file_1.name if uploaded_file_1 else "Sample Data A"
source_2 = uploaded_file_2.name if uploaded_file_2 else "Sample Data B"

# -----------------------------------------------------------------------------
# CHART RENDERING ENGINE (Works for any dataset)
# -----------------------------------------------------------------------------
def render_dataset_dashboard(df, title, source_name, prefix):
    st.header(title)
    st.caption(f"Source: `{source_name}`")
    
    # --- DYNAMIC COLUMN MAPPING UI ---
    st.markdown("###### ⚙️ Map Your Columns")
    with st.expander("Expand to map dataset columns to charts", expanded=True):
        cols = ["Not Selected"] + list(df.columns)
        c1, c2, c3 = st.columns(3)
        
        # Auto-detect defaults
        def_loc = find_default_col(df.columns, ['city', 'state', 'local', 'region', 'area_name'])
        def_price = find_default_col(df.columns, ['price', 'cost', 'amount', 'budget'])
        def_area = find_default_col(df.columns, ['area', 'sqft', 'size', 'build'])
        def_type = find_default_col(df.columns, ['type', 'category', 'bhk'])
        def_yield = find_default_col(df.columns, ['yield', 'rent', 'roi'])
        def_attr = find_default_col(df.columns, ['attract', 'score', 'rating'])

        col_loc = c1.selectbox("Location/State/City Col", cols, index=cols.index(def_loc) if def_loc in cols else 0, key=f"{prefix}_loc")
        col_price = c2.selectbox("Sale Price Col", cols, index=cols.index(def_price) if def_price in cols else 0, key=f"{prefix}_prc")
        col_area = c3.selectbox("Build Up Area Col", cols, index=cols.index(def_area) if def_area in cols else 0, key=f"{prefix}_area")
        
        c4, c5, c6 = st.columns(3)
        col_type = c4.selectbox("Property Type Col", cols, index=cols.index(def_type) if def_type in cols else 0, key=f"{prefix}_typ")
        col_yield = c5.selectbox("Rental Yield Col", cols, index=cols.index(def_yield) if def_yield in cols else 0, key=f"{prefix}_yld")
        col_attr = c6.selectbox("Attraction Score Col", cols, index=cols.index(def_attr) if def_attr in cols else 0, key=f"{prefix}_att")

    st.markdown("---")

    # --- KPIs ---
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Properties", f"{len(df):,}")
    if col_price != "Not Selected" and pd.api.types.is_numeric_dtype(df[col_price]):
        k2.metric("Average Price", f"₹{df[col_price].mean():,.0f}")
    if col_area != "Not Selected" and pd.api.types.is_numeric_dtype(df[col_area]):
        k3.metric("Average Area", f"{df[col_area].mean():,.0f} sqft")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CHARTS ---
    # 1. Location Distribution & Property Type
    ch1, ch2 = st.columns(2)
    with ch1:
        if col_loc != "Not Selected":
            fig1 = px.pie(df, names=col_loc, title="Distribution by Location", template="plotly_dark", hole=0.4)
            st.plotly_chart(fig1, width="stretch")
    with ch2:
        if col_type != "Not Selected":
            fig2 = px.pie(df, names=col_type, title="Property Type Distribution", template="plotly_dark")
            st.plotly_chart(fig2, width="stretch")

    # 2. Avg Price by Locality
    if col_loc != "Not Selected" and col_price != "Not Selected":
        avg_price_df = df.groupby(col_loc)[col_price].mean().reset_index().sort_values(by=col_price, ascending=False).head(15)
        fig3 = px.bar(avg_price_df, x=col_loc, y=col_price, title="Avg Sale Price by Locality/State", template="plotly_dark", color=col_price, color_continuous_scale="Viridis")
        st.plotly_chart(fig3, width="stretch")

    # 3. Build Up Area vs Sale Price (Scatter)
    if col_area != "Not Selected" and col_price != "Not Selected":
        fig4 = px.scatter(df, x=col_area, y=col_price, color=col_type if col_type != "Not Selected" else None, 
                          title="Build-Up Area vs Sale Price", template="plotly_dark", opacity=0.7)
        st.plotly_chart(fig4, width="stretch")

    # 4. Budget Range (Price Histogram)
    if col_price != "Not Selected":
        fig5 = px.histogram(df, x=col_price, nbins=30, title="Budget Range Distribution", template="plotly_dark", color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig5, width="stretch")

    # 5. Rental Yield & Attraction Score
    ch3, ch4 = st.columns(2)
    with ch3:
        if col_loc != "Not Selected" and col_yield != "Not Selected":
            yld_df = df.groupby(col_loc)[col_yield].mean().reset_index()
            fig6 = px.bar(yld_df, x=col_loc, y=col_yield, title="Avg Rental Yield by Locality", template="plotly_dark")
            st.plotly_chart(fig6, width="stretch")
    with ch4:
        if col_loc != "Not Selected" and col_attr != "Not Selected":
            attr_df = df.groupby(col_loc)[col_attr].mean().reset_index()
            fig7 = px.bar(attr_df, x=col_loc, y=col_attr, title="Avg Attraction Score by Locality", template="plotly_dark", color_discrete_sequence=['#00CC96'])
            st.plotly_chart(fig7, width="stretch")


# -----------------------------------------------------------------------------
# MAIN DASHBOARD LAYOUT
# -----------------------------------------------------------------------------
st.title("⚖️ Compare Real Estate Datasets")
st.markdown("Upload your CSVs. The app will automatically map columns (or you can map them yourself) to generate insights.")

col1, col2 = st.columns(2)

with col1:
    render_dataset_dashboard(df1, "Dataset A", source_1, "d1")

with col2:
    render_dataset_dashboard(df2, "Dataset B", source_2, "d2")

st.markdown("---")
st.subheader("Raw Data Preview")
tab1, tab2 = st.tabs(["Dataset A Preview", "Dataset B Preview"])
with tab1:
    st.dataframe(df1.head(10), width="stretch")
with tab2:
    st.dataframe(df2.head(10), width="stretch")
