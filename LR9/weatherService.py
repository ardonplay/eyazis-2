# import the module
import python_weather

import asyncio
import os

async def get_weather(city) -> None:
  # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
  async with python_weather.Client(unit=python_weather.METRIC) as client:
    # fetch a weather forecast from a city
    weather = await client.get(city)
    
    return weather.temperature
    # returns the current day's forecast temperature (int)
