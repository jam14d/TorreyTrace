import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

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

# Merge
combined_df = pd.merge_asof(
    tide_df.sort_values("Timestamp"),
    wave_df.sort_values("Timestamp"),
    on="Timestamp",
    direction="nearest",
    tolerance=pd.Timedelta("1H")
)
combined_df["Temperature"] = pd.Series(hourly_temp).values
combined_df.dropna(subset=["Tide_Height_m", "Wave_Height_m", "Temperature"], inplace=True)

# Check data
print("Combined data points:", len(combined_df))
print(combined_df[['Tide_Height_m', 'Wave_Height_m', 'Temperature']].describe())

if combined_df.empty:
    raise ValueError("No valid data to animate.")

# Ocean grid setup
x = np.linspace(0, 10, 100)
y = np.linspace(0, 10, 100)  
X, Y = np.meshgrid(x, y)

# 3D figure setup
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

ax.set_xlim(0, 10)
ax.set_ylim(0, 20)
ax.set_zlim(-1, 3)
ax.set_xlabel("Beach Width (X)")
ax.set_ylabel("Wave Direction (Y)")
ax.set_zlabel("Water Height (Z)")
ax.view_init(elev=30, azim=-135)
fig.patch.set_facecolor('#002b36')
ax.set_facecolor('#001f33')

surf = [None]
time_text = ax.text2D(0.05, 0.95, "", transform=ax.transAxes, color='white')

# Temperature to blue shades (cooler = deep blue, warmer = soft aqua)
def temp_to_color(temp):
    if temp < 16:
        return "#2c3e50"  # cold indigo
    elif temp < 18:
        return "#3b5998"  # navy
    elif temp < 20:
        return "#4a90e2"  # medium blue
    elif temp < 22:
        return "#50c9ba"  # teal
    else:
        return "#8be0d4"  # aqua (warmest)


# Animation update
def update(frame):
    row = combined_df.iloc[frame]
    tide = row["Tide_Height_m"]
    wave = row["Wave_Height_m"]
    temp = row["Temperature"]
    timestamp = row["Timestamp"]

    # Adjust wave spacing
    Z = tide + wave * np.sin(2 * np.pi * (X - 0.1 * frame) / 4)

    # Add subtle noise for realism
    noise_strength = 0.05 * wave
    noise = noise_strength * np.random.normal(size=X.shape)
    Z += noise

    if surf[0] is not None:
        surf[0].remove()

    # Top wave surface
    surf[0] = ax.plot_surface(
        X, Y, Z,
        cmap=None,
        color=temp_to_color(temp),
        edgecolor='none',
        alpha=0.9
    )

    time_text.set_text(timestamp.strftime('%b %d, %Y %H:%M'))

    print(f"[{frame}] Tide={tide:.2f}, Wave={wave:.2f}, Temp={temp:.1f}, Time={timestamp}")
    print("Z min/max:", np.min(Z), np.max(Z))

    return surf[0], time_text

# Animate
ani = animation.FuncAnimation(
    fig,
    update,
    frames=len(combined_df),
    interval=100,
    blit=False
)

plt.tight_layout()
plt.show()
