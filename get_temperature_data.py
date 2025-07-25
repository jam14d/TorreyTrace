import requests
import pandas as pd
import datetime

def fetch_temperature_data(latitude=32.9211, longitude=-117.2526, days=7):
    """
    Fetch daily max/min temperature for Torrey Pines from Open-Meteo.
    Returns a DataFrame with date, max, and min temps.
    """
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days - 1)

    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={latitude}&longitude={longitude}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&daily=temperature_2m_max,temperature_2m_min"
        f"&timezone=America%2FLos_Angeles"
    )

    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame({
        'Date': pd.to_datetime(data['daily']['time']),
        'Temp_Max': data['daily']['temperature_2m_max'],
        'Temp_Min': data['daily']['temperature_2m_min'],
    })

    return df

# Preview if run directly
if __name__ == "__main__":
    df = fetch_temperature_data()
    print(df)

    # quick plot comment out whenevea
    import matplotlib.pyplot as plt
    df.plot(x='Date', y=['Temp_Max', 'Temp_Min'], marker='o', title="Torrey Pines Temps")
    plt.ylabel("°C")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
