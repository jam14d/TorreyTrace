import pandas as pd
import datetime
import pandas as pd
import datetime
import requests

url = "https://www.ndbc.noaa.gov/data/realtime2/46225.txt"
response = requests.get(url)

# print("Raw NOAA data preview:")
# print("\n".join(response.text.splitlines()[:10])) 


def fetch_wave_data(station_id="46225", days=7):
    """
    Fetch wave height data from NOAA NDBC for given station (default: Torrey Pines Outer).
    Returns DataFrame with 'Timestamp' and 'Wave_Height_m'.
    """

    url = f"https://www.ndbc.noaa.gov/data/realtime2/{station_id}.txt"

    try:
        df = pd.read_csv(
            url,
            delim_whitespace=True,
            header=None,
            skiprows=2,  # Skip the two comment/header lines
            na_values=['MM', '99.00', '9999.0']
        )
    except Exception as e:
        print(f"Error fetching wave data: {e}")
        return pd.DataFrame(columns=["Timestamp", "Wave_Height_m"])

    # Assign column names from NOAA documentation
    df.columns = [
        "YY", "MM", "DD", "hh", "mm", "WDIR", "WSPD", "GST", "WVHT", "DPD",
        "APD", "MWD", "PRES", "ATMP", "WTMP", "DEWP", "VIS", "PTDY", "TIDE"
    ]

    # Filter and create datetime
    df = df[['YY', 'MM', 'DD', 'hh', 'mm', 'WVHT']].dropna()
    df['Timestamp'] = pd.to_datetime(dict(
        year=df['YY'], month=df['MM'], day=df['DD'],
        hour=df['hh'], minute=df['mm']
    ), errors='coerce')

    df = df[['Timestamp', 'WVHT']].dropna()
    df.rename(columns={'WVHT': 'Wave_Height_m'}, inplace=True)

    # Filter by time
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    df = df[df['Timestamp'] >= cutoff]

    return df.reset_index(drop=True)


if __name__ == "__main__":
    wave_df = fetch_wave_data()
    print(wave_df.head())
    print(f"\nWave data rows: {len(wave_df)}")
    print(f"Date range: {wave_df['Timestamp'].min()} to {wave_df['Timestamp'].max()}")
