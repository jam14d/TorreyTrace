import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta

from get_tide_data import fetch_tide_data
from get_wave_data import fetch_wave_data
from get_temperature_data import fetch_temperature_data
from utils import interpolate_temperature_to_hours


print("Fetching data...")
tide_df = fetch_tide_data()
wave_df = fetch_wave_data()
temp_df = fetch_temperature_data()

hourly_temp = interpolate_temperature_to_hours(tide_df, temp_df)

# convert timestamps
tide_df['Timestamp'] = pd.to_datetime(tide_df['Timestamp'])
wave_df['Timestamp'] = pd.to_datetime(wave_df['Timestamp'])

# print summaries
print("\nTIDE DATA=")
print(tide_df.info())
print("Tide time range:", tide_df['Timestamp'].min(), "→", tide_df['Timestamp'].max())
print("Tide frequency (mode):", tide_df['Timestamp'].diff().mode()[0])

print("\nWAVE DATA")
print(wave_df.info())
print("Wave time range:", wave_df['Timestamp'].min(), "→", wave_df['Timestamp'].max())
print("Wave frequency (mode):", wave_df['Timestamp'].diff().mode()[0])

print("\nTEMPERATURE INTERPOLATION")
print(f"Temperature array length: {len(hourly_temp)}")
print("Sample temps:", hourly_temp[:5])

#Visual check of timestamp overlap 
plt.figure(figsize=(12, 3))
plt.plot(tide_df['Timestamp'], [1]*len(tide_df), '|', label='Tide', color='blue')
plt.plot(wave_df['Timestamp'], [2]*len(wave_df), '|', label='Wave', color='green')
plt.yticks([1, 2], ['Tide', 'Wave'])
plt.title("Timestamp Distribution")
plt.legend()
plt.tight_layout()
plt.show()

# check merge
merged_df = pd.merge_asof(
    tide_df.sort_values("Timestamp"),
    wave_df.sort_values("Timestamp"),
    on="Timestamp",
    direction="nearest",
    tolerance=pd.Timedelta("1H")
)
merged_df["Temperature"] = pd.Series(hourly_temp).values

#Add time diff for validation
nearest_wave_df = wave_df.set_index("Timestamp").sort_index()
merged_df["Wave_Match_Timestamp"] = merged_df["Timestamp"].apply(
    lambda t: nearest_wave_df.index.get_indexer([t], method='nearest')[0]
)
merged_df["Wave_Match_Timestamp"] = nearest_wave_df.index[merged_df["Wave_Match_Timestamp"]].values
merged_df["Wave_Timestamp_Diff"] = (merged_df["Timestamp"] - merged_df["Wave_Match_Timestamp"]).abs()

#  Display a few rows for manual inspection 
print("\n MERGED SAMPLE ")
print(merged_df[['Timestamp', 'Tide_Height_m', 'Wave_Height_m', 'Temperature', 'Wave_Match_Timestamp', 'Wave_Timestamp_Diff']].head(10))

#  Summary stats 
print("\n MERGE QUALITY ")
print("Total merged rows:", len(merged_df))
print("Missing values per column:")
print(merged_df.isna().sum())

print("\nMax time difference in matching wave readings:", merged_df["Wave_Timestamp_Diff"].max())

