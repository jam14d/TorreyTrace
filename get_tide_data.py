import requests
import pandas as pd
import datetime

def fetch_tide_data(station_id="9410230", days=7):
    """
    Fetch hourly tide data from NOAA for the past `days` days.
    Returns a pandas DataFrame with timestamps and tide height in meters.
    """
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days - 1)

    # Format dates for API
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')

    # NOAA API setup
    url = (
        f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
        f"begin_date={start_str}&end_date={end_str}"
        f"&station={station_id}&product=predictions&datum=MLLW"
        f"&interval=h&units=metric&time_zone=lst_ldt&format=json"
    )

    # Fetch and parse data
    response = requests.get(url)
    data = response.json()
    tide_df = pd.DataFrame(data["predictions"])
    tide_df['t'] = pd.to_datetime(tide_df['t'])
    tide_df['v'] = tide_df['v'].astype(float)
    tide_df.rename(columns={'t': 'Timestamp', 'v': 'Tide_Height_m'}, inplace=True)
    
    return tide_df

if __name__ == "__main__":
    tide_df = fetch_tide_data()
    print(tide_df.head())
