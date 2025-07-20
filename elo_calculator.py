import pandas as pd
import matplotlib.pyplot as plt

# Constants
STARTING_ELO = 1500
K_FACTOR_PROVISIONAL = 40 # For fights during the first 3 fights
K_FACTOR_NEW = 32         # For fights 4-10
K_FACTOR_ESTABLISHED = 24 # For fights 11-20
K_FACTOR_VETERAN = 16     # For fights 21+
K_FACTOR_TITLE = 50

class EloCalculator:
    """Manages fighter ratings with all advanced rules."""
    def __init__(self):
        self.ratings = {}
        self.fight_counts = {}
        self.streaks = {}
        self.last_fight_dates = {}

    def get_k_factor(self, fighter_name, is_title_fight):
        if is_title_fight: return K_FACTOR_TITLE
        count = self.fight_counts.get(fighter_name, 0)
        # We now have a provisional period for the first 3 fights
        if count <= 3: return K_FACTOR_PROVISIONAL
        elif count <= 10: return K_FACTOR_NEW
        elif count <= 20: return K_FACTOR_ESTABLISHED
        else: return K_FACTOR_VETERAN

    # ... (the rest of the methods like get_victory_multiplier, _apply_inactivity_decay, etc., remain the same) ...

    def update_ratings(self, fight_row):
        fighter_a, fighter_b, winner = fight_row['Fighter A'], fight_row['Fighter B'], fight_row['Winner']
        # ... (rest of the variable assignments) ...

        self._apply_inactivity_decay(fighter_a, weight_class, current_date)
        self._apply_inactivity_decay(fighter_b, weight_class, current_date)

        rating_a = self.ratings.setdefault(fighter_a, {}).setdefault(weight_class, STARTING_ELO)
        rating_b = self.ratings.setdefault(fighter_b, {}).setdefault(weight_class, STARTING_ELO)

        # Get the base K-factor for each fighter
        k_a = self.get_k_factor(fighter_a, is_title_fight)
        k_b = self.get_k_factor(fighter_b, is_title_fight)

        # --- NEW: Provisional K-Factor Adjustment ---
        # If a provisional fighter is fighting an established one, reduce the provisional K-factor
        is_a_provisional = self.fight_counts.get(fighter_a, 0) <= 3
        is_b_provisional = self.fight_counts.get(fighter_b, 0) <= 3

        if is_a_provisional and not is_b_provisional:
            k_a = K_FACTOR_NEW # Use a slightly lower K-factor
        if is_b_provisional and not is_a_provisional:
            k_b = K_FACTOR_NEW # Use a slightly lower K-factor

        # --- End of New Logic ---


# --- Main Execution Block ---
if __name__ == "__main__":
    df = pd.read_csv('ufc_fight_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by='Date', inplace=True)
    df['Weight Class'].fillna('Open Weight', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    calculator = EloCalculator()
    historical_ratings = []
    
    print("✅ Running simulation, please wait...")
    for i, fight in df.iterrows():
        calculator.update_ratings(fight)
        fighter_a, fighter_b, wc = fight['Fighter A'], fight['Fighter B'], fight['Weight Class']
        historical_ratings.append({'Date': fight['Date'], 'Fighter': fighter_a, 'Division': wc, 'Elo': calculator.ratings[fighter_a][wc]})
        historical_ratings.append({'Date': fight['Date'], 'Fighter': fighter_b, 'Division': wc, 'Elo': calculator.ratings[fighter_b][wc]})
    print("✅ Simulation complete!")
    
    final_ratings_list = []
    for fighter, divisions in calculator.ratings.items():
        for division, rating in divisions.items():
            final_ratings_list.append({
                'Fighter': fighter, 'Division': division, 'Elo': int(rating),
                'Fight Count': calculator.fight_counts.get(fighter, 0)
            })
    ratings_df = pd.DataFrame(final_ratings_list)
    history_df = pd.DataFrame(historical_ratings)

    # --- Interactive Menu Loop ---
    while True:
        print("\n--- UFC Elo Project Menu ---")
        print("1. View Divisional Rankings")
        print("2. Plot a Fighter's Career")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            display_rankings(ratings_df)
        elif choice == '2':
            plot_fighter(history_df)
        elif choice == '3':
            print("Exiting project. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")