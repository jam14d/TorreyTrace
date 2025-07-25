import pandas as pd
import matplotlib.pyplot as plt

from get_tide_data import fetch_tide_data
from get_wave_data import fetch_wave_data
from get_temperature_data import fetch_temperature_data
from utils import interpolate_temperature_to_hours

# Fetch and prepare data
tide_df = fetch_tide_data()
wave_df = fetch_wave_data()
temp_df = fetch_temperature_data()
hourly_temp = interpolate_temperature_to_hours(tide_df, temp_df)

tide_df['Timestamp'] = pd.to_datetime(tide_df['Timestamp'])
wave_df['Timestamp'] = pd.to_datetime(wave_df['Timestamp'])

# Merge dataframes
combined_df = pd.merge_asof(
    tide_df.sort_values("Timestamp"),
    wave_df.sort_values("Timestamp"),
    on="Timestamp",
    direction="nearest",
    tolerance=pd.Timedelta("1H")
)
combined_df["Temperature"] = pd.Series(hourly_temp).values
combined_df.dropna(subset=["Tide_Height_m", "Wave_Height_m"], inplace=True)

if combined_df.empty:
    raise ValueError("No data to plot.")

# Plot tide and wave height over time
def plot_metric_trends(df):
    plt.figure(figsize=(14, 6))

    plt.plot(df['Timestamp'], df['Tide_Height_m'], label='Tide Height (m)', color='dodgerblue')
    plt.plot(df['Timestamp'], df['Wave_Height_m'], label='Wave Height (m)', color='seagreen')

    plt.title('Tide and Wave Height Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('Height (m)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

plot_metric_trends(combined_df)
