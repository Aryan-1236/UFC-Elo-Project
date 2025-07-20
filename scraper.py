import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_event_links():
    """Finds and returns a list of all individual UFC event page links."""
    url = "http://ufcstats.com/statistics/events/completed?page=all"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        event_rows = soup.find_all('tr', class_='b-statistics__table-row')
        event_links = [row.find('a')['href'] for row in event_rows if row.find('a')]
        print(f"Successfully found {len(event_links)} event links.")
        return event_links
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

def parse_event_page(event_url):
    """Parses a single event page based on the confirmed HTML structure."""
    fights_data = []
    event_date = None
    try:
        response = requests.get(event_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        details_list = soup.select('ul.b-list__box-list li')
        for item in details_list:
            if "Date:" in item.get_text():
                event_date = item.get_text(strip=True).replace("Date:", "").strip()
                break
        
        fight_rows = soup.select('tr.b-fight-details__table-row[data-link]')
        for row in fight_rows:
            try:
                columns = row.select('td')
                if len(columns) < 10: continue

                # Extract Names
                fighter_a = columns[1].select('p')[0].get_text(strip=True)
                fighter_b = columns[1].select('p')[1].get_text(strip=True)
                
                # Final, Corrected Winner Logic
                winner = "Draw/NC"
                win_flag = columns[0].select_one('a.b-flag_style_green')
                if win_flag:
                    winner = fighter_a
                
                # Extract other details
                weight_class = columns[6].get_text(strip=True)
                method = columns[7].get_text(strip=True)
                round_ = columns[8].get_text(strip=True)
                time = columns[9].get_text(strip=True)

                fights_data.append({
                    'Date': event_date, 'Fighter A': fighter_a, 'Fighter B': fighter_b,
                    'Winner': winner, 'Weight Class': weight_class, 'Method': method,
                    'Round': round_, 'Time': time
                })
            except IndexError:
                continue
        return fights_data
    except Exception as e:
        print(f"Could not scrape {event_url}. Error: {e}")
        return None

# Final execution block to create the CSV
if __name__ == "__main__":
    event_links = get_event_links()
    all_fights_data = []
    
    if event_links:
        for i, link in enumerate(event_links):
            print(f"Scraping ({i+1}/{len(event_links)}): {link.split('/')[-1]}")
            fights_from_event = parse_event_page(link)
            if fights_from_event:
                all_fights_data.extend(fights_from_event)
            time.sleep(0.5)

        if all_fights_data:
            df = pd.DataFrame(all_fights_data)
            file_path = 'ufc_fight_data.csv'
            df.to_csv(file_path, index=False)
            print(f"\n✅ Scraping complete! All fight data saved to '{file_path}'.")
            print(f"Total fights scraped: {len(df)}")
        else:
            print("\n❌ Scraping finished, but no data was collected.")