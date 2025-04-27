from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import html
import re
import time
from datetime import datetime, timedelta

class TrafficScraper:
    def __init__(self, places, urls, headless=True):
        if not places or not urls:
            raise ValueError("Places and URLs must be provided.")
        if len(places) != len(urls):
            raise ValueError("The number of places and URLs must match.")
        
        self.places = places
        self.urls = urls
        self.data = {}
        
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        if headless:
            chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        self.chrome_options = chrome_options

    def scrape(self):
        traffic_data = {}
        for idx, url in enumerate(self.urls):
            driver = webdriver.Chrome(options=self.chrome_options)
            try:
                driver.get(url)
                time.sleep(3)  # Wait for the page to load
                page_source = driver.page_source
            except Exception as e:
                driver.quit()
                raise ConnectionError(f"Failed to load page {url}: {str(e)}")
            driver.quit()
            
            soup = BS(page_source, "html.parser")
            try:
                directions_text = re.search(r'"(Directions from.*?)"', str(soup)).group(1)
            except AttributeError:
                raise ValueError(f"Could not find directions text on page {url}")
            
            section = soup.find('div', attrs={'aria-label': html.unescape(directions_text)})
            if section is None:
                raise ValueError(f"Could not find traffic section for {self.places[idx]}")
            
            for span in section.find_all('span'):
                trial_text = span.get_text()
                match = re.search(r'(([0-9]+) hr \(([0-9.]+) km\))|(([0-9]+) min \(([0-9.]+) km\))|(([0-9]+) hr ([0-9]+) min \(([0-9.]+) km\))', trial_text)
                if match:
                    if match.group(2) and match.group(3):
                        # X hr (Y km)
                        traffic_data[self.places[idx]] = {
                            "time": int(match.group(2)) * 60,
                            "distance": float(match.group(3))
                        }
                    elif match.group(5) and match.group(6):
                        # X min (Y km)
                        traffic_data[self.places[idx]] = {
                            "time": int(match.group(5)),
                            "distance": float(match.group(6))
                        }
                    elif match.group(8) and match.group(9) and match.group(10):
                        # X hr Y min (Z km)
                        traffic_data[self.places[idx]] = {
                            "time": int(match.group(8)) * 60 + int(match.group(9)),
                            "distance": float(match.group(10))
                        }
        self.data = traffic_data
        return traffic_data

    def to_dataframe(self):
        if not self.data:
            raise ValueError("No data available. Please run scrape() first.")
        
        altered_data = {}
        for place, info in self.data.items():
            altered_data[place + " time"] = info["time"]
            altered_data[place + " distance"] = info["distance"]
        
        df = pd.DataFrame([altered_data])
        return df

    def to_csv(self, filename):
        df = self.to_dataframe()
        df.to_csv(filename, index=False)
        print(f"Data exported to {filename}")

    def start_scraping(self, duration_minutes=30, interval_minutes=5):
        """Repeatedly scrapes data for a certain duration at fixed intervals."""
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        all_dataframes = []

        while datetime.now() < end_time:
            print(f"Scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.scrape()
            df = self.to_dataframe()
            df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            all_dataframes.append(df)
            time.sleep(interval_minutes * 60)  # Sleep for 'interval_minutes' minutes

        final_df = pd.concat(all_dataframes, ignore_index=True)
        return final_df
