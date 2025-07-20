Yes, I've checked the code. It's very well-structured, but it has one critical error that will cause it to crash and it's also missing the advanced "Streak Bonus" rules we discussed previously.

Here's the breakdown and the final, fully-featured code.

-----

### **Critical Error: Missing Functions**

The script will crash when you select option `1` or `2` from the menu. This is because the menu calls the functions `display_rankings()` and `plot_fighter()`, but those functions are not defined anywhere in the code you provided.

### **The Final, Fully-Featured Code**

Below is the complete and final version of `elo_calculator.py`. It fixes the crash by including the missing functions and also upgrades the `EloCalculator` class to include **every advanced feature we've discussed**:

  * ✅ Ring Rust (Inactivity Decay)
  * ✅ Elite Opponent Bonus
  * ✅ Momentum/Streak Bonus

**Action:** Replace the entire contents of your `elo_calculator.py` file with this definitive version.

```python
import pandas as pd
import matplotlib.pyplot as plt

# --- Elo Calculation Engine (v3.1 - All Features) ---

# Constants
STARTING_ELO = 1500
K_FACTOR_NEW = 36
K_FACTOR_ESTABLISHED = 28
K_FACTOR_VETERAN = 20
K_FACTOR_TITLE = 50
ELITE_ELO_THRESHOLD = 1700
ELITE_BONUS = 1.1
STREAK_BONUS_PER_WIN = 0.05
INACTIVITY_DAYS = 540 # Approx. 18 months
INACTIVITY_PENALTY = 25

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
        if count < 5: return K_FACTOR_NEW
        elif count < 15: return K_FACTOR_ESTABLISHED
        else: return K_FACTOR_VETERAN

    def get_victory_multiplier(self, method, round_):
        method_lower = str(method).lower()
        if 'ko' in method_lower or 'tko' in method_lower or 'submission' in method_lower:
            if round_ == '1': return 1.6
            if round_ in ['2', '3']: return 1.4
            if round_ in ['4', '5']: return 1.2
        if 'unanimous' in method_lower: return 1.1
        return 1.0

    def _apply_inactivity_decay(self, fighter, weight_class, current_date):
        last_fight_date = self.last_fight_dates.get(fighter)
        if last_fight_date and (current_date - last_fight_date).days > INACTIVITY_DAYS:
            if fighter in self.ratings and weight_class in self.ratings[fighter]:
                self.ratings[fighter][weight_class] -= INACTIVITY_PENALTY

    def update_ratings(self, fight_row):
        fighter_a, fighter_b, winner = fight_row['Fighter A'], fight_row['Fighter B'], fight_row['Winner']
        weight_class, method, round_, current_date = fight_row['Weight Class'], fight_row['Method'], fight_row['Round'], fight_row['Date']
        is_title_fight = "Title" in weight_class

        self._apply_inactivity_decay(fighter_a, weight_class, current_date)
        self._apply_inactivity_decay(fighter_b, weight_class, current_date)

        rating_a = self.ratings.setdefault(fighter_a, {}).setdefault(weight_class, STARTING_ELO)
        rating_b = self.ratings.setdefault(fighter_b, {}).setdefault(weight_class, STARTING_ELO)

        expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        if winner == fighter_a: score_a = 1.0
        elif winner == fighter_b: score_a = 0.0
        else: score_a = 0.5

        elite_bonus = ELITE_BONUS if (winner == fighter_a and rating_b >= ELITE_ELO_THRESHOLD) or \
                                     (winner == fighter_b and rating_a >= ELITE_ELO_THRESHOLD) else 1.0

        streak_bonus = 1.0
        if winner == fighter_a and self.streaks.get(fighter_b, 0) > 0:
            streak_bonus = (1 + self.streaks[fighter_b] * STREAK_BONUS_PER_WIN)
        elif winner == fighter_b and self.streaks.get(fighter_a, 0) > 0:
            streak_bonus = (1 + self.streaks[fighter_a] * STREAK_BONUS_PER_WIN)

        k_a, k_b = self.get_k_factor(fighter_a, is_title_fight), self.get_k_factor(fighter_b, is_title_fight)
        victory_mult = self.get_victory_multiplier(method, round_) if winner != "Draw/NC" else 1.0
        
        change_a = victory_mult * elite_bonus * streak_bonus * k_a * (score_a - expected_a)
        change_b = victory_mult * elite_bonus * streak_bonus * k_b * ((1-score_a) - (1-expected_a))

        self.ratings[fighter_a][weight_class] = rating_a + change_a
        self.ratings[fighter_b][weight_class] = rating_b + change_b

        self._update_streaks(fighter_a, fighter_b, winner)
        self.fight_counts[fighter_a] = self.fight_counts.get(fighter_a, 0) + 1
        self.fight_counts[fighter_b] = self.fight_counts.get(fighter_b, 0) + 1
        self.last_fight_dates[fighter_a] = current_date
        self.last_fight_dates[fighter_b] = current_date

    def _update_streaks(self, fighter_a, fighter_b, winner):
        current_streak_a, current_streak_b = self.streaks.get(fighter_a, 0), self.streaks.get(fighter_b, 0)
        if winner == fighter_a:
            self.streaks[fighter_a] = (current_streak_a + 1) if current_streak_a > 0 else 1
            self.streaks[fighter_b] = (current_streak_b - 1) if current_streak_b < 0 else -1
        elif winner == fighter_b:
            self.streaks[fighter_b] = (current_streak_b + 1) if current_streak_b > 0 else 1
            self.streaks[fighter_a] = (current_streak_a - 1) if current_streak_a < 0 else -1
        else:
            self.streaks[fighter_a], self.streaks[fighter_b] = 0, 0

# --- Helper functions for the menu (These were missing) ---
def display_rankings(ratings_df):
    division = input("Enter the weight class to rank (e.g., Lightweight, Heavyweight): ")
    filtered_df = ratings_df[
        (ratings_df['Division'].str.contains(division, case=False)) &
        (ratings_df['Fight Count'] >= 5)
    ].sort_values(by='Elo', ascending=False)
    
    if filtered_df.empty:
        print(f"\nNo fighters found for '{division}' with 5 or more fights.")
    else:
        print(f"\n--- Top 15 in {division} ---")
        print(filtered_df.head(15).to_string(index=False))

def plot_fighter(history_df):
    fighter_name = input("Enter the full name of the fighter to plot: ")
    fighter_history = history_df[history_df['Fighter'].str.lower() == fighter_name.lower()]
    
    if fighter_history.empty:
        print(f"\nCould not find fight history for '{fighter_name}'.")
    else:
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.figure(figsize=(12, 7))
        for division in fighter_history['Division'].unique():
            division_history = fighter_history[fighter_history['Division'] == division]
            plt.plot(division_history['Date'], division_history['Elo'], marker='o', linestyle='-', label=f"{division} Elo")
        plt.title(f"Elo Rating History for {fighter_name}", fontsize=16)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Elo Rating", fontsize=12)
        plt.legend()
        plt.tight_layout()
        plt.show()

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
```