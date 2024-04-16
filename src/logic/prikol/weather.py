import requests

def get_weather(api_key="e8c4e195e035f4befb6d2f044b5cfcc5", city="Москва"):
    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    )
    data = response.json()
    main_data = data["main"]
    temperature = round(main_data["temp"])
    feels_like = f"{round(main_data['feels_like'])}°C"
    humidity = main_data["humidity"]
    data_to_return = f"В Москве {temperature}°C, по ощущениям {feels_like}"
    data_to_return += (
        f", на улице слызько" if int(humidity) > 75 else f", на улице сухо и мерзко"
    )
    return data_to_return
