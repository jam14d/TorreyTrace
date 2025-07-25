import pandas as pd

def interpolate_temperature_to_hours(tide_df, temp_df):
    """
    Interpolates daily average temperature to match hourly tide timestamps.
    Returns a Series of interpolated hourly temperatures.
    """
    # Compute average daily temperature
    temp_df['Temp_Avg'] = (temp_df['Temp_Max'] + temp_df['Temp_Min']) / 2

    # Set daily timestamps at midnight
    temp_series = pd.Series(
        data=temp_df['Temp_Avg'].values,
        index=pd.to_datetime(temp_df['Date'])
    )

    # Reindex to tide timestamps and interpolate
    hourly_temp = temp_series.reindex(
        tide_df['Timestamp'],
        method=None
    ).interpolate(method='time')

    return hourly_temp
