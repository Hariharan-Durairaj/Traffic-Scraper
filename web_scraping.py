from TrafficScraper import TrafficScraper  # Adjust the import based on your file name

# Define the places and their corresponding Google Maps URLs (after clicking "Details" button)
places = [
    "adelaide city to airport",
    "adelaide city to gawler"
]

urls = [
    "https://www.google.com/maps/dir/Adelaide,+South+Australia/Adelaide+Airport+(ADL),+Sir+Richard+Williams+Ave,+Adelaide+Airport+SA+5950/@-34.9348381,138.5247744,19873m/am=t/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x6ab735c7c526b33f:0x4033654628ec640!2m2!1d138.6007456!2d-34.9284989!1m5!1m1!1s0x6ab0c53c8a1e29cf:0xf03365545b8f0f0!2m2!1d138.5312017!2d-34.946237!3e0?authuser=0&entry=ttu&g_ep=EgoyMDI1MDQyMy4wIKXMDSoASAFQAw%3D%3D",
    "https://www.google.com/maps/dir/Adelaide,+South+Australia/Gawler+SA/@-34.7532006,138.4905843,79669m/am=t/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x6ab735c7c526b33f:0x4033654628ec640!2m2!1d138.6007456!2d-34.9284989!1m5!1m1!1s0x6ab9ffc3074c8283:0xd5b804a15262918b!2m2!1d138.7490985!2d-34.5972074!3e0?authuser=0&entry=ttu&g_ep=EgoyMDI1MDQyMy4wIKXMDSoASAFQAw%3D%3D",
]

# Create a scraper object
scraper = TrafficScraper(places, urls, headless=True)  # headless=True means the browser won't open

# If you want to see the browser while scraping, set `headless=False` like this:
# scraper = TrafficScraper(places, urls, headless=False)


# Scrape the current traffic data once
traffic_data = scraper.scrape()
print(traffic_data)

# Convert to a DataFrame
df = scraper.to_dataframe()
print(df)

# Save to a CSV file
scraper.to_csv("traffic_data_now.csv")

# Scrape traffic data repeatedly for 10 minutes every 5 minutes
long_run_df = scraper.start_scraping(duration_minutes=10, interval_minutes=5)

# Save the long collected dataset
long_run_df.to_csv("traffic_data_over_time.csv", index=False)