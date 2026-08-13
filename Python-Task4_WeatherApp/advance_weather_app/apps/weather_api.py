import os
import json
import urllib.parse
import urllib.request
import urllib.error

from pathlib import Path
from dotenv import load_dotenv


# Load .env from the project root
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


class WeatherAPIError(Exception):
    """Custom exception for weather API errors."""
    pass


class WeatherAPI:

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")

        if not self.api_key:
            raise WeatherAPIError(
                "OPENWEATHER_API_KEY is not configured."
            )
    # =====================================================
    # HTTP REQUEST
    # =====================================================

    def _request(self, endpoint, params):
        params["appid"] = self.api_key

        query = urllib.parse.urlencode(params)

        url = f"{self.BASE_URL}/{endpoint}?{query}"

        try:
            with urllib.request.urlopen(
                url,
                timeout=10
            ) as response:

                data = response.read().decode("utf-8")

                return json.loads(data)

        except urllib.error.HTTPError as error:

            if error.code == 401:
                raise WeatherAPIError(
                    "Invalid OpenWeather API key."
                )

            if error.code == 404:
                raise WeatherAPIError(
                    "Location not found."
                )

            if error.code == 429:
                raise WeatherAPIError(
                    "Weather API request limit exceeded."
                )

            raise WeatherAPIError(
                f"Weather API error: HTTP {error.code}"
            )

        except urllib.error.URLError:
            raise WeatherAPIError(
                "Unable to connect to the weather service."
            )

        except Exception as error:
            raise WeatherAPIError(
                f"Request failed: {error}"
            )

    # =====================================================
    # LOCATION
    # =====================================================

    def get_location(self):
        """
        Detect approximate location using IP.
        """

        try:

            with urllib.request.urlopen(
                "https://ipapi.co/json/",
                timeout=8
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            latitude = data.get("latitude")
            longitude = data.get("longitude")

            if latitude is None or longitude is None:
                raise WeatherAPIError(
                    "Unable to detect your location."
                )

            return latitude, longitude

        except urllib.error.URLError:
            raise WeatherAPIError(
                "Unable to detect your location."
            )

        except Exception as error:

            if isinstance(error, WeatherAPIError):
                raise

            raise WeatherAPIError(
                f"Location detection failed: {error}"
            )

    # =====================================================
    # CURRENT WEATHER
    # =====================================================

    def get_current(
        self,
        query=None,
        use_location=False,
        units="metric"
    ):

        params = {
            "units": units
        }

        if use_location:

            latitude, longitude = self.get_location()

            params["lat"] = latitude
            params["lon"] = longitude

        else:

            if not query:
                raise WeatherAPIError(
                    "A city or location is required."
                )

            params["q"] = query

        return self._request(
            "weather",
            params
        )

    # =====================================================
    # FORECAST
    # =====================================================

    def get_forecast(
        self,
        query=None,
        use_location=False,
        units="metric"
    ):

        params = {
            "units": units
        }

        if use_location:

            latitude, longitude = self.get_location()

            params["lat"] = latitude
            params["lon"] = longitude

        else:

            if not query:
                raise WeatherAPIError(
                    "A city or location is required."
                )

            params["q"] = query

        return self._request(
            "forecast",
            params
        )

    # =====================================================
    # GET EVERYTHING
    # =====================================================

    def get_weather(
        self,
        query=None,
        use_location=False,
        units="metric"
    ):

        current = self.get_current(
            query=query,
            use_location=use_location,
            units=units
        )

        forecast = self.get_forecast(
            query=query,
            use_location=use_location,
            units=units
        )

        return current, forecast