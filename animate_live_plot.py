import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd

from get_tide_data import fetch_tide_data
from get_wave_data import fetch_wave_data
from get_temperature_data import fetch_temperature_data
from utils import interpolate_temperature_to_hours


#animated correlation plot -- honestly kind of weird i don't know why i thought this would be cool lol. 
#i think we can work with live plotting correlation in some other way in addition to the sine 3d plot, i'll think on this
#test

# fetch
tide_df = fetch_tide_data()
wave_df = fetch_wave_data()
temp_df = fetch_temperature_data()
hourly_temp = interpolate_temperature_to_hours(tide_df, temp_df)

# Ensure Timestamp columns are proper
tide_df['Timestamp'] = pd.to_datetime(tide_df['Timestamp'])
wave_df['Timestamp'] = pd.to_datetime(wave_df['Timestamp'])

# Merge on timestamp (nearest)
combined_df = pd.merge_asof(
    tide_df.sort_values("Timestamp"),
    wave_df.sort_values("Timestamp"),
    on="Timestamp",
    direction="nearest",
    tolerance=pd.Timedelta("1H")
)

# Add temperature and clean
combined_df["Temperature"] = pd.Series(hourly_temp).values
combined_df.dropna(subset=["Tide_Height_m", "Wave_Height_m", "Temperature"], inplace=True)

# safeguard to check for data
if combined_df.empty:
    raise ValueError("No valid data to plot. Check tide, wave, and temperature sources.")

# Set up the animated scatter plot
fig, ax = plt.subplots(figsize=(7, 5))
sc = ax.scatter([], [], c=[], cmap='coolwarm', s=50)

# Set axis limits with padding
ax.set_xlim(combined_df['Tide_Height_m'].min() - 0.2, combined_df['Tide_Height_m'].max() + 0.2)
ax.set_ylim(combined_df['Wave_Height_m'].min() - 0.2, combined_df['Wave_Height_m'].max() + 0.2)
ax.set_xlabel("Tide Height (m)")
ax.set_ylabel("Wave Height (m)")
title = ax.set_title("Tide vs. Wave Height — Torrey Pines")

# Add live timestamp display
time_text = ax.text(0.05, 0.95, "", transform=ax.transAxes, ha="left", va="top", fontsize=10, bbox=dict(facecolor='white', alpha=0.8))

# Animation update function
def update(frame):
    data = combined_df.iloc[:frame+1]
    x = data["Tide_Height_m"]
    y = data["Wave_Height_m"]
    temps = data["Temperature"]

    sc.set_offsets(list(zip(x, y)))
    sc.set_array(temps)
    time_text.set_text(data.iloc[-1]["Timestamp"].strftime("%b %d %Y %H:%M"))

    return sc, time_text

# Run animation 
ani = animation.FuncAnimation(
    fig,
    update,
    frames=len(combined_df),
    interval=100,
    blit=False
)

plt.tight_layout()
plt.show()
