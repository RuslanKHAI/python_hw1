import httpx
import json
import asyncio
from joblib import Parallel, delayed

async def async_weather_data(cities, api_key):
    temperatures = {}
    
    async with httpx.AsyncClient() as client:
        tasks = []
        
        for city in cities:
            tasks.append(client.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'))

        try:
            responses = await asyncio.gather(*tasks)

            
            results = Parallel(n_jobs=-1)(delayed(_process_response)(response) for response in responses)
            
            for city_name, temp in results:
                temperatures[city_name] = temp
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Некорректный API ключ, Пожалуйста вставье корерктный ключ."
            else:
                return (f"Error HTTP: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            return f"Request Error (Ошибка запроса) : {e}"
        except Exception as e:
            return f"Непредвиденная ошибка: {e}"

    return temperatures

def _process_response(response): 
    stat_weather_data = response.json()
    temp = stat_weather_data['main']['temp']
    city_name = stat_weather_data['name'] 
    return city_name, temp