import streamlit as st
import pandas as pd
import plotly.express as px
import logging
import atexit

# --- Logging Setup ---
logging.basicConfig(
    filename='project1.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def clear_log():
    with open('project1.log', 'w') as f:
        f.truncate(0)
atexit.register(clear_log)

# --- Data Loading and Preparation ---
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Steven-Alvarado/Global-Temperature-Analysis/refs/heads/main/GlobalTemperatures.csv"
    df = pd.read_csv(url)
    df['dt'] = pd.to_datetime(df['dt'])
    df = df.rename(columns={
        'dt': 'Date',
        'LandAverageTemperature': 'Land_Avg_Temp',
        'LandMaxTemperature': 'Land_Max_Temp',
        'LandMinTemperature': 'Land_Min_Temp',
        'LandAndOceanAverageTemperature': 'Land_Ocean_Avg_Temp'
    })
    df['Year'] = df['Date'].dt.year
    return df

df = load_data()

# --- Streamlit UI ---
st.title("Global Temperature Analysis Dashboard")
st.markdown("Explore how average land temperatures have changed over time.")

st.sidebar.title("Filters")
year_range = st.sidebar.slider(
    "Select Range in years",
    int(df['Year'].min()),
    int(df['Year'].max()),
    (1850, 2015)
)

column_options = [
    'Land_Avg_Temp',
    'Land_Max_Temp',
    'Land_Min_Temp',
    'Land_Ocean_Avg_Temp'
]
selected_cols = st.sidebar.multiselect(
    'Select temperature types to display:',
    column_options,
    default=['Land_Avg_Temp']
)

# --- Data Filtering ---
filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
temp_for_each_year = filtered_df.groupby('Year')[selected_cols].mean().reset_index()

# --- Chart Type Selection ---
chart_type = st.sidebar.radio('Chart type:', ['Line', 'Bar', 'Area'], index=0)

# --- Plotting ---
def plot_chart(df, x, y_cols, chart_type):
    if chart_type == 'Line':
        fig = px.line(df, x=x, y=y_cols, title='Global Temperature Trends Over Time',
                      labels={'Year': 'Year', 'value': 'Temperature (°C)', 'variable': 'Temperature Type'})
        fig.update_traces(mode='lines+markers')
    elif chart_type == 'Bar':
        fig = px.bar(df, x=x, y=y_cols, barmode='group',
                     title='Global Temperature Trends Over Time',
                     labels={'Year': 'Year', 'value': 'Temperature (°C)', 'variable': 'Temperature Type'})
    elif chart_type == 'Area':
        fig = px.area(df, x=x, y=y_cols, title='Global Temperature Trends Over Time',
                      labels={'Year': 'Year', 'value': 'Temperature (°C)', 'variable': 'Temperature Type'})
    else:
        fig = px.line(df, x=x, y=y_cols)
    return fig

if selected_cols:
    fig = plot_chart(temp_for_each_year, 'Year', selected_cols, chart_type)
    st.markdown("### Temperature Trends Over Years")
    st.plotly_chart(fig, use_container_width=True)

    # --- Hottest and Coldest Year Annotations ---
    for col in selected_cols:
        temp_year = temp_for_each_year[['Year', col]].dropna()
        if not temp_year.empty:
            hottest = temp_year.loc[temp_year[col].idxmax()]
            coldest = temp_year.loc[temp_year[col].idxmin()]
            st.markdown(f"**{col.replace('_', ' ')}**")
            st.markdown(f"Hottest Year: {int(hottest['Year'])} ({hottest[col]:.2f} °C)")
            st.markdown(f"Coldest Year: {int(coldest['Year'])} ({coldest[col]:.2f} °C)")

# --- Raw Data Display ---
st.write("### Raw Data")
with st.expander("Show Filtered Data"):
    st.dataframe(filtered_df)

# --- Log user input selections ---
logger.info(f"User selected year range: {year_range}")
logger.info(f"User selected temperature columns: {selected_cols}")
logger.info(f"User selected chart type: {chart_type}")