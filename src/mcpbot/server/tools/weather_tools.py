from fastmcp import Context
import httpx
from typing import List
import asyncio
from mcp import types

def register_weather_tools(mcp):
    @mcp.tool(
        name="get_weather",
        description="Get current weather for one or multiple cities",
        tags={"weather", "api"},
        meta={"version": "1.2", "author": "support-team"},  # Custom metadata
        annotations=types.ToolAnnotations(
            title="The Weather Tool",
            readOnlyHint=True,  # If true, the tool does not modify its environment.
            destructiveHint=False,  # If true, the tool may perform destructive updates to its environment.
            idempotentHint=True,  # If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
            openWorldHint=False,
            # If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
        )
    )
    async def get_weather(cities: List[str], ctx: Context) -> dict:
        """
        Get weather information for multiple cities.

        Args:
            cities: List of city names (e.g., ["Paris", "London", "Tokyo"])

        Returns:
            Dictionary with weather data for each city
        """
        results = {}

        async with httpx.AsyncClient() as client:
            tasks = []
            for city in cities:
                tasks.append(fetch_weather_for_city(client, city))

            weather_data = await asyncio.gather(*tasks, return_exceptions=True)

            for city, data in zip(cities, weather_data):
                if isinstance(data, Exception):
                    results[city] = {"error": str(data)}
                else:
                    results[city] = data

        return results


async def fetch_weather_for_city(client: httpx.AsyncClient, city: str) -> dict:
    """Fetch weather data for a single city using Open-Meteo API (free, no key needed)"""
    try:
        # First, get coordinates for the city using geocoding
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = await client.get(geocoding_url)
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return {"error": f"City '{city}' not found"}

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]

        # Get weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
        weather_response = await client.get(weather_url)
        weather_data = weather_response.json()

        current = weather_data["current"]

        return {
            "city": location["name"],
            "country": location.get("country", "Unknown"),
            "temperature": f"{current['temperature_2m']}°C",
            "feels_like": f"{current['apparent_temperature']}°C",
            "humidity": f"{current['relative_humidity_2m']}%",
            "wind_speed": f"{current['wind_speed_10m']} km/h",
            "precipitation": f"{current['precipitation']} mm",
            "weather_code": current['weather_code']
        }

    except Exception as e:
        return {"error": f"Failed to fetch weather: {str(e)}"}