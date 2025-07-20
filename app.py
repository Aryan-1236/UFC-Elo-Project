import streamlit as st
import pandas as pd
from elo_calculator import EloCalculator

# Use the full width of the page for our app and set a title
st.set_page_config(layout="wide", page_title="UFC Elo Ratings")

@st.cache_data
def load_and_run_simulation():
    """
    This function loads the fight data, runs the entire Elo simulation,
    and returns the final dataframes. It's cached so it only runs once.
    """
    df = pd.read_csv('ufc_fight_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by='Date', inplace=True)
    df['Weight Class'].fillna('Open Weight', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    calculator = EloCalculator()
    historical_ratings = []
    
    for i, fight in df.iterrows():
        calculator.update_ratings(fight)
        fighter_a, fighter_b, wc = fight['Fighter A'], fight['Fighter B'], fight['Weight Class']
        historical_ratings.append({'Date': fight['Date'], 'Fighter': fighter_a, 'Division': wc, 'Elo': calculator.ratings[fighter_a][wc]})
        historical_ratings.append({'Date': fight['Date'], 'Fighter': fighter_b, 'Division': wc, 'Elo': calculator.ratings[fighter_b][wc]})
    
    final_ratings_list = []
    for fighter, divisions in calculator.ratings.items():
        for division, rating in divisions.items():
            final_ratings_list.append({
                'Fighter': fighter, 'Division': division, 'Elo': int(rating),
                'Fight Count': calculator.fight_counts.get(fighter, 0)
            })
    ratings_df = pd.DataFrame(final_ratings_list)
    history_df = pd.DataFrame(historical_ratings)
    
    return ratings_df, history_df

# --- Main App ---
st.title("🥊 UFC Elo Rating & Analytics")

# Load data using our cached function
ratings_df, history_df = load_and_run_simulation()

# --- Sidebar Controls ---
st.sidebar.header("Controls")

# Create a dropdown for division selection
divisions = ["Pound-for-Pound"] + sorted(ratings_df['Division'].unique().tolist())
selected_division = st.sidebar.selectbox("Select a Weight Class", divisions)

# Create a text input for fighter search
fighter_to_plot = st.sidebar.text_input("Search for a Fighter to Plot their Career")

# --- Main Page Display ---

# Display the rankings based on the dropdown selection
st.header(f"Rankings: {selected_division}")

if selected_division == "Pound-for-Pound":
    display_df = ratings_df[ratings_df['Fight Count'] >= 10].sort_values(by="Elo", ascending=False)
else:
    display_df = ratings_df[
        (ratings_df['Division'] == selected_division) &
        (ratings_df['Fight Count'] >= 5)
    ].sort_values(by="Elo", ascending=False)

st.dataframe(display_df)


# Display the plot if a fighter name has been entered
if fighter_to_plot:
    st.header(f"Career Trajectory for {fighter_to_plot}")
    
    fighter_history = history_df[history_df['Fighter'].str.lower() == fighter_to_plot.lower()]
    
    if fighter_history.empty:
        st.warning("Fighter not found. Please check the spelling.")
    else:
        # We need to import matplotlib here for Streamlit's pyplot functionality
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(12, 7))
        plt.style.use('seaborn-v0_8-whitegrid')
        
        for division in fighter_history['Division'].unique():
            division_history = fighter_history[fighter_history['Division'] == division]
            ax.plot(division_history['Date'], division_history['Elo'], marker='o', linestyle='-', label=f"{division} Elo")
            
        ax.set_title(f"Elo Rating History for {fighter_to_plot}", fontsize=16)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Elo Rating", fontsize=12)
        ax.legend()
        plt.tight_layout()
        
        # Display the plot in the Streamlit app
        st.pyplot(fig)