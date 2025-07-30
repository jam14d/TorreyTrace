import pandas as pd
import matplotlib.pyplot as plt

from get_tide_data import fetch_tide_data
from get_wave_data import fetch_wave_data
from get_temperature_data import fetch_temperature_data
from utils import interpolate_temperature_to_hours


def plot_wave_height_zoomed(df, advisory_start, advisory_end, wave_spikes):
    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=False)

    # Ensure the data is sorted by time
    df = df.sort_values('Timestamp')

    # Define time windows relative to the last timestamp
    last_timestamp = df['Timestamp'].max()
    start_1w = last_timestamp - pd.Timedelta(days=7)
    start_2d = last_timestamp - pd.Timedelta(days=2)

    # 1. Past 1 week
    data_1w = df[df['Timestamp'] >= start_1w]
    spikes_1w = wave_spikes[wave_spikes['Timestamp'] >= start_1w]
    axes[0].plot(data_1w['Timestamp'], data_1w['Wave_Height_m'], color='seagreen', label='Wave Height (m)')
    axes[0].scatter(spikes_1w['Timestamp'], spikes_1w['Wave_Height_m'], color='red', label='Wave Spike', zorder=5)
    axes[0].axvspan(advisory_start, advisory_end, color='red', alpha=0.1, label='Tsunami Advisory')
    axes[0].set_xlim(start_1w, last_timestamp)
    axes[0].set_ylabel('Wave Height (m)')
    axes[0].set_title('Wave Height - Past 1 Week')
    axes[0].legend()
    axes[0].grid(True)

    # 2. Past 2 days (zoomed in)
    data_2d = df[df['Timestamp'] >= start_2d]
    spikes_2d = wave_spikes[wave_spikes['Timestamp'] >= start_2d]
    axes[1].plot(data_2d['Timestamp'], data_2d['Wave_Height_m'], color='seagreen', label='Wave Height (m)')
    axes[1].scatter(spikes_2d['Timestamp'], spikes_2d['Wave_Height_m'], color='red', label='Wave Spike', zorder=5)
    axes[1].axvspan(advisory_start, advisory_end, color='red', alpha=0.1)
    axes[1].set_xlim(start_2d, last_timestamp)
    axes[1].set_ylabel('Wave Height (m)')
    axes[1].set_title('Wave Height - Past 2 Days (Zoomed)')
    axes[1].legend()
    axes[1].grid(True)

    plt.suptitle('Wave Height with Tsunami Advisory and Wave Spikes Highlighted', fontsize=14)
    plt.xlabel('Timestamp (UTC)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()



def main():
    # Fetch and prepare data
    tide_df = fetch_tide_data()
    wave_df = fetch_wave_data()
    temp_df = fetch_temperature_data()
    hourly_temp = interpolate_temperature_to_hours(tide_df, temp_df)

    tide_df['Timestamp'] = pd.to_datetime(tide_df['Timestamp'], utc=True)
    wave_df['Timestamp'] = pd.to_datetime(wave_df['Timestamp'], utc=True)

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

    # Advisory window
    advisory_start = pd.to_datetime("2025-07-29 12:00", utc=True)
    advisory_end = pd.to_datetime("2025-07-31 12:00", utc=True)

    # Detect wave spikes
    wave_spike_threshold = combined_df['Wave_Height_m'].mean() + 2 * combined_df['Wave_Height_m'].std()
    wave_spikes = combined_df[combined_df['Wave_Height_m'] > wave_spike_threshold]

    # Plot zoomed views
    plot_wave_height_zoomed(combined_df, advisory_start, advisory_end, wave_spikes)


if __name__ == "__main__":
    main()
