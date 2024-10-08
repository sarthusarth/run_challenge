import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import os

# File to store the runs data
RUNS_FILE = 'runs_data.csv'

# Load existing runs from file or create empty DataFrame
@st.cache_data
def load_runs():
    if os.path.exists(RUNS_FILE):
        df = pd.read_csv(RUNS_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date  # Convert to date
        return df
    return pd.DataFrame(columns=['Date', 'Name', 'Distance'])

# Save runs to file
def save_runs(runs_df):
    runs_df['Date'] = runs_df['Date'].astype(str)  # Convert date to string for saving
    runs_df.to_csv(RUNS_FILE, index=False)
    runs_df['Date'] = pd.to_datetime(runs_df['Date']).dt.date  # Convert back to date

# Initialize runs
runs = load_runs()

# Fixed list of names with associated colors
NAMES_COLORS = {
    'Hannah': '#FF9999',     # Light Red
    'Morgan': '#66B2FF',     # Light Blue
    'Josephine': '#99FF99',  # Light Green
    'Nazar': '#FFCC99',      # Light Orange
    'Sarthak': '#CC99FF'     # Light Purple
}

def add_run():
    global runs
    new_run = pd.DataFrame({
        'Date': [st.session_state.date],
        'Name': [st.session_state.name],
        'Distance': [st.session_state.distance]
    })
    runs = pd.concat([runs, new_run], ignore_index=True)
    save_runs(runs)
    st.cache_data.clear()

def delete_run(index):
    global runs
    runs = runs.drop(index).reset_index(drop=True)
    save_runs(runs)
    st.cache_data.clear()

st.title('Run Tracker')

# Sidebar for adding new runs
st.sidebar.header('Log a New Run')
with st.sidebar.form(key='log_run'):
    st.date_input('Date', key='date', value=date.today())
    st.selectbox('Name', options=list(NAMES_COLORS.keys()), key='name')
    st.number_input('Distance (km)', min_value=5, step=1, key='distance')
    submit_button = st.form_submit_button(label='Log Run', on_click=add_run)

# Main page content
tab1, tab2 = st.tabs(['Leaderboard', 'All Runs'])

with tab1:
    st.header('Leaderboard')
    if not runs.empty:
        leaderboard = runs.groupby('Name').agg({
            'Distance': ['sum', 'count']
        }).reset_index()
        leaderboard.columns = ['Name', 'Total Distance', 'Number of Runs']
        leaderboard = leaderboard.sort_values('Total Distance', ascending=False)
        leaderboard['Average Distance'] = leaderboard['Total Distance'] / leaderboard['Number of Runs']
        
        # Display leaderboard without color
        st.dataframe(leaderboard)

        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Total Distance Bar Chart
            fig_distance = px.bar(leaderboard, x='Name', y='Total Distance', 
                                  title='Total Distance by Runner',
                                  color='Name', color_discrete_map=NAMES_COLORS)
            st.plotly_chart(fig_distance)

        with col2:
            # Number of Runs Bar Chart
            fig_runs = px.bar(leaderboard, x='Name', y='Number of Runs', 
                              title='Number of Runs by Runner',
                              color='Name', color_discrete_map=NAMES_COLORS)
            st.plotly_chart(fig_runs)

        # Average Distance per Run
        fig_avg = px.scatter(leaderboard, x='Name', y='Average Distance', 
                             size='Number of Runs', color='Name',
                             title='Average Distance per Run',
                             color_discrete_map=NAMES_COLORS)
        st.plotly_chart(fig_avg)

        # Runner Progress Over Time
        runner_progress = runs.copy()
        runner_progress = runner_progress.sort_values('Date')
        runner_progress['Cumulative Distance'] = runner_progress.groupby('Name')['Distance'].cumsum()

        fig_progress = px.line(runner_progress, x='Date', y='Cumulative Distance', color='Name',
                               title='Runner Progress Over Time',
                               color_discrete_map=NAMES_COLORS)
        st.plotly_chart(fig_progress)

    else:
        st.write('No data available for leaderboard yet.')

with tab2:
    st.header('All Runs')
    if not runs.empty:
        for index, run in runs.iterrows():
            col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
            with col1:
                st.write(f"Date: {run['Date']}")
            with col2:
                st.write(f"Name: {run['Name']}")
            with col3:
                st.write(f"Distance: {run['Distance']} km")
            with col4:
                if st.button('Delete', key=f'delete_{index}'):
                    delete_run(index)
                    st.rerun()
    else:
        st.write('No runs logged yet.')

# Display color legend
st.sidebar.header('Color Legend')
for name, color in NAMES_COLORS.items():
    st.sidebar.markdown(f'<p style="color:{color};">■ {name}</p>', unsafe_allow_html=True)