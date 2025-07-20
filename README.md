# UFC Elo Rating & Analytics Project

This is a sports analytics project that calculates the historical Elo ratings for every fighter in the UFC's history. The project includes a web scraper to gather data, a sophisticated custom Elo engine, and an interactive web application built with Streamlit to display the results.

## Features

- **Historical Data Scraper**: A Python script (`scraper.py`) that scrapes every fight from every event in UFC history from UFCStats.com.
- **Advanced Elo Engine**: The core of the project (`elo_calculator.py`) uses a custom Elo rating system with several advanced rules:
  - **Dynamic K-Factor**: New fighters have a higher K-factor that decreases as they gain more experience.
  - **Round-based Victory Multipliers**: Bigger bonuses are awarded for earlier finishes.
  - **Inactivity Decay**: A small Elo penalty is applied for "ring rust" if a fighter has a long layoff (18+ months).
  - **Provisional Ratings**: A special K-factor adjustment is used for a fighter's first few bouts to ensure their rating is established fairly.
- **Interactive Web Application**: An easy-to-use web app (`app.py`) built with Streamlit that allows you to:
  - View the current top 15 rankings for every weight class.
  - See a Pound-for-Pound ranking of the top fighters.
  - Search for any fighter and view a plot of their entire career Elo rating history.

## How to Run

1.  **Set up the environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

    _(Note: You may need to create a `requirements.txt` file first with `pip freeze > requirements.txt`)_

2.  **Generate the data (if needed):**

    ```bash
    python scraper.py
    ```

3.  **Run the interactive web application:**
    ```bash
    streamlit run app.py
    ```
