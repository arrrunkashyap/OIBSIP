import threading
import urllib.request
from datetime import datetime
from io import BytesIO

import customtkinter as ctk
from PIL import Image

from .weather_api import WeatherAPI, WeatherAPIError


# ---------------------------------------------------------
# Appearance
# ---------------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class WeatherApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # -------------------------------------------------
        # Window
        # -------------------------------------------------

        self.title("Advanced Weather Dashboard")
        self.geometry("1350x850")
        self.minsize(1050, 700)

        # -------------------------------------------------
        # State
        # -------------------------------------------------

        self.api = None
        self.api_error = None

        self.current_data = None
        self.forecast_data = None

        self.last_query = None
        self.use_location = True

        self.units = "metric"
        self.loading = False

        self.search_history = []

        # -------------------------------------------------
        # API initialization
        # -------------------------------------------------

        try:
            self.api = WeatherAPI()

        except WeatherAPIError as error:
            self.api_error = str(error)

        # -------------------------------------------------
        # Build interface
        # -------------------------------------------------

        self.build_ui()

        # Enter key = search
        self.bind(
            "<Return>",
            lambda event: self.search_weather()
        )

        # -------------------------------------------------
        # Initial location detection
        # -------------------------------------------------

        if self.api_error:

            self.show_error(
                self.api_error
            )

        else:

            self.after(
                500,
                self.detect_location
            )

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):

        self.grid_columnconfigure(
            0,
            weight=1
        )

        self.grid_rowconfigure(
            2,
            weight=1
        )

                # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = ctk.CTkFrame(
            self,
            height=82,
            corner_radius=0,
            fg_color=("gray95", "gray10")
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        header.grid_columnconfigure(1, weight=1)

        # -------------------------------------------------
        # BRAND
        # -------------------------------------------------

        brand_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        brand_frame.grid(
            row=0,
            column=0,
            padx=(24, 18),
            pady=12,
            sticky="w"
        )

        ctk.CTkLabel(
            brand_frame,
            text="☁",
            font=ctk.CTkFont(size=30)
        ).pack(
            side="left",
            padx=(0, 8)
        )

        title_frame = ctk.CTkFrame(
            brand_frame,
            fg_color="transparent"
        )

        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="WEATHER",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Advanced Dashboard",
            text_color="gray",
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w")

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        search_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        search_frame.grid(
            row=0,
            column=1,
            padx=8,
            sticky="ew"
        )

        search_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            height=40,
            corner_radius=10,
            placeholder_text="Search city or ZIP / postal code..."
        )

        self.search_entry.grid(
            row=0,
            column=0,
            padx=(0, 6),
            sticky="ew"
        )

        self.search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            width=88,
            height=40,
            corner_radius=10,
            command=self.search_weather
        )

        self.search_button.grid(
            row=0,
            column=1
        )

        # -------------------------------------------------
        # ACTIONS
        # -------------------------------------------------

        action_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        action_frame.grid(
            row=0,
            column=2,
            padx=(8, 20),
            sticky="e"
        )

        self.location_button = ctk.CTkButton(
            action_frame,
            text="📍",
            width=42,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=18),
            command=self.detect_location
        )

        self.location_button.grid(
            row=0,
            column=0,
            padx=3
        )

        self.unit_switch = ctk.CTkSegmentedButton(
            action_frame,
            values=["°C", "°F"],
            width=100,
            height=40,
            command=self.change_unit
        )

        self.unit_switch.set("°C")

        self.unit_switch.grid(
            row=0,
            column=1,
            padx=3
        )

        self.theme_button = ctk.CTkButton(
            action_frame,
            text="☀",
            width=42,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=18),
            command=self.toggle_theme
        )

        self.theme_button.grid(
            row=0,
            column=2,
            padx=3
        )

        self.refresh_button = ctk.CTkButton(
            action_frame,
            text="↻",
            width=42,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=21),
            command=self.refresh_weather
        )

        self.refresh_button.grid(
            row=0,
            column=3,
            padx=3
        )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        self.status = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w"
        )

        self.status.grid(
            row=1,
            column=0,
            padx=25,
            pady=6,
            sticky="ew"
        )

        # -------------------------------------------------
        # MAIN SCROLLABLE AREA
        # -------------------------------------------------

        self.body = ctk.CTkScrollableFrame(
            self,
            corner_radius=0
        )

        self.body.grid(
            row=2,
            column=0,
            padx=12,
            pady=5,
            sticky="nsew"
        )

        self.body.grid_columnconfigure(
            (0, 1),
            weight=1
        )

        # Build sections

        self.build_current_card()

        self.build_metrics()

        self.build_history()

        self.build_forecasts()

        # =====================================================
    # CURRENT WEATHER CARD
    # =====================================================

    def build_current_card(self):

        self.current_card = ctk.CTkFrame(
            self.body,
            corner_radius=22,
            fg_color=("gray95", "gray12")
        )

        self.current_card.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=6,
            pady=(8, 12),
            sticky="ew"
        )

        # Responsive columns
        self.current_card.grid_columnconfigure(
            1,
            weight=1
        )

        # -------------------------------------------------
        # WEATHER ICON
        # -------------------------------------------------

        icon_frame = ctk.CTkFrame(
            self.current_card,
            width=150,
            height=150,
            corner_radius=20,
            fg_color=("gray90", "gray18")
        )

        icon_frame.grid(
            row=0,
            column=0,
            rowspan=3,
            padx=(22, 20),
            pady=22
        )

        icon_frame.grid_propagate(False)

        self.weather_icon = ctk.CTkLabel(
            icon_frame,
            text="☁",
            font=ctk.CTkFont(
                size=80
            )
        )

        self.weather_icon.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        self.location_label = ctk.CTkLabel(
            self.current_card,
            text="Detecting location...",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        self.location_label.grid(
            row=0,
            column=1,
            sticky="w",
            padx=(0, 15),
            pady=(25, 2)
        )

        # -------------------------------------------------
        # CONDITION
        # -------------------------------------------------

        self.condition_label = ctk.CTkLabel(
            self.current_card,
            text="Current conditions",
            text_color=("gray35", "gray70"),
            font=ctk.CTkFont(
                size=17
            )
        )

        self.condition_label.grid(
            row=1,
            column=1,
            sticky="w",
            padx=(0, 15)
        )

        # -------------------------------------------------
        # TEMPERATURE
        # -------------------------------------------------

        self.temperature_label = ctk.CTkLabel(
            self.current_card,
            text="--",
            font=ctk.CTkFont(
                size=58,
                weight="bold"
            )
        )

        self.temperature_label.grid(
            row=2,
            column=1,
            sticky="w",
            padx=(0, 15),
            pady=(0, 25)
        )

        # -------------------------------------------------
        # UPDATED INFORMATION
        # -------------------------------------------------

        updated_frame = ctk.CTkFrame(
            self.current_card,
            fg_color="transparent"
        )

        updated_frame.grid(
            row=0,
            column=2,
            rowspan=3,
            padx=(10, 25),
            pady=25,
            sticky="ne"
        )

        ctk.CTkLabel(
            updated_frame,
            text="LAST UPDATED",
            text_color=("gray45", "gray60"),
            font=ctk.CTkFont(
                size=10,
                weight="bold"
            )
        ).pack(
            anchor="e"
        )

        self.updated_label = ctk.CTkLabel(
            updated_frame,
            text="--",
            text_color=("gray35", "gray70"),
            font=ctk.CTkFont(
                size=13
            )
        )

        self.updated_label.pack(
            anchor="e",
            pady=(3, 0)
        )
 
        # =====================================================
    # WEATHER METRICS
    # =====================================================

    def build_metrics(self):

        metrics_frame = ctk.CTkFrame(
            self.body,
            fg_color="transparent"
        )

        metrics_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=6,
            pady=(0, 12),
            sticky="ew"
        )

        # Four cards per row
        for column in range(4):
            metrics_frame.grid_columnconfigure(
                column,
                weight=1
            )

        metrics = [
            ("feels", "🌡", "Feels Like", "--"),
            ("humidity", "💧", "Humidity", "--"),
            ("wind", "💨", "Wind", "--"),
            ("pressure", "⏱", "Pressure", "--"),
            ("visibility", "👁", "Visibility", "--"),
            ("clouds", "☁", "Clouds", "--"),
            ("sunrise", "🌅", "Sunrise", "--"),
            ("sunset", "🌇", "Sunset", "--"),
        ]

        self.metric_values = {}

        for index, (key, icon, title, value) in enumerate(metrics):

            row = index // 4
            column = index % 4

            card = ctk.CTkFrame(
                metrics_frame,
                height=110,
                corner_radius=16,
                fg_color=("gray95", "gray14")
            )

            card.grid(
                row=row,
                column=column,
                padx=5,
                pady=5,
                sticky="nsew"
            )

            card.grid_propagate(False)

            # Icon
            ctk.CTkLabel(
                card,
                text=icon,
                font=ctk.CTkFont(
                    size=22
                )
            ).pack(
                pady=(10, 0)
            )

            # Title
            ctk.CTkLabel(
                card,
                text=title,
                text_color=("gray40", "gray65"),
                font=ctk.CTkFont(
                    size=11,
                    weight="bold"
                )
            ).pack(
                pady=(2, 0)
            )

            # Value
            value_label = ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(
                    size=17,
                    weight="bold"
                )
            )

            value_label.pack(
                pady=(1, 8)
            )

            self.metric_values[key] = value_label
    # =====================================================
    # SEARCH HISTORY
    # =====================================================

    def build_history(self):

        ctk.CTkLabel(
            self.body,
            text="Recent Searches",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            padx=7,
            pady=(18, 6),
            sticky="w"
        )

        self.history_frame = ctk.CTkFrame(
            self.body,
            corner_radius=12
        )

        self.history_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=6,
            pady=4,
            sticky="ew"
        )

        self.history_label = ctk.CTkLabel(
            self.history_frame,
            text="Search a city to build your history.",
            text_color="gray"
        )

        self.history_label.pack(
            padx=14,
            pady=10,
            anchor="w"
        )

    def update_history(self, query):

        if not query:
            return

        query = query.strip()

        # Remove duplicate

        self.search_history = [
            item
            for item in self.search_history
            if item.lower() != query.lower()
        ]

        # Add to beginning

        self.search_history.insert(
            0,
            query
        )

        # Keep only last 5

        self.search_history = self.search_history[:5]

        # Clear old widgets

        for widget in self.history_frame.winfo_children():

            widget.destroy()

        # Create buttons

        for item in self.search_history:

            button = ctk.CTkButton(
                self.history_frame,
                text=f"↻  {item}",
                height=32,
                fg_color="transparent",
                hover_color=(
                    "gray80",
                    "gray25"
                ),
                text_color=(
                    "gray20",
                    "gray90"
                ),
                anchor="w",
                command=lambda q=item:
                self.search_from_history(q)
            )

            button.pack(
                fill="x",
                padx=6,
                pady=2
            )

    def search_from_history(self, query):

        self.search_entry.delete(
            0,
            "end"
        )

        self.search_entry.insert(
            0,
            query
        )

        self.last_query = query

        self.use_location = False

        self.load_weather(
            query=query,
            use_location=False
        )

    # =====================================================
    # FORECAST SECTIONS
    # =====================================================

    def build_forecasts(self):

        # Next 6 hours

        ctk.CTkLabel(
            self.body,
            text="Next 6 Hours",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            padx=7,
            pady=(20, 8),
            sticky="w"
        )

        self.hourly_frame = ctk.CTkFrame(
            self.body,
            fg_color="transparent"
        )

        self.hourly_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=6
        )

        # 5 day

        ctk.CTkLabel(
            self.body,
            text="5-Day Forecast",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            padx=7,
            pady=(20, 8),
            sticky="w"
        )

        self.daily_frame = ctk.CTkFrame(
            self.body,
            fg_color="transparent"
        )

        self.daily_frame.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=6
        )

    # =====================================================
    # SEARCH
    # =====================================================

    def search_weather(self):

        query = self.search_entry.get().strip()

        if not query:

            self.show_error(
                "Enter a city name or ZIP / postal code."
            )

            return

        self.last_query = query

        self.use_location = False

        self.load_weather(
            query=query,
            use_location=False
        )

    # =====================================================
    # LOCATION
    # =====================================================

    def detect_location(self):

        self.use_location = True

        self.load_weather(
            query=None,
            use_location=True
        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_weather(self):

        if self.use_location:

            self.load_weather(
                query=None,
                use_location=True
            )

        elif self.last_query:

            self.load_weather(
                query=self.last_query,
                use_location=False
            )

        else:

            self.detect_location()

    # =====================================================
    # UNIT
    # =====================================================

    def change_unit(self, value):

        if value == "°F":

            self.units = "imperial"

        else:

            self.units = "metric"

        self.refresh_weather()

    # =====================================================
    # THEME
    # =====================================================

    def toggle_theme(self):

        current = ctk.get_appearance_mode()

        if current == "Dark":

            ctk.set_appearance_mode(
                "light"
            )

            self.theme_button.configure(
                text="☾"
            )

        else:

            ctk.set_appearance_mode(
                "dark"
            )

            self.theme_button.configure(
                text="☀"
            )

    # =====================================================
    # LOAD WEATHER
    # =====================================================

    def load_weather(
        self,
        query,
        use_location
    ):

        if not self.api:

            self.show_error(
                self.api_error or
                "Weather API is not configured."
            )

            return

        if self.loading:

            return

        self.loading = True

        # Disable controls

        self.search_button.configure(
            state="disabled"
        )

        self.location_button.configure(
            state="disabled"
        )

        self.refresh_button.configure(
            state="disabled"
        )

        self.status.configure(
            text="● Fetching weather data..."
        )

        # Background thread

        def worker():

            try:

                current, forecast = \
                    self.api.get_weather(
                        query=query,
                        use_location=use_location,
                        units=self.units
                    )

                self.after(
                    0,
                    lambda:
                    self.update_weather(
                        current,
                        forecast
                    )
                )

            except WeatherAPIError as error:

                self.after(
                    0,
                    lambda:
                    self.show_error(
                        str(error)
                    )
                )

            except Exception as error:

                self.after(
                    0,
                    lambda:
                    self.show_error(
                        f"Unexpected error: {error}"
                    )
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    # =====================================================
    # UPDATE WEATHER
    # =====================================================

    def update_weather(
        self,
        current,
        forecast
    ):

        self.current_data = current

        self.forecast_data = forecast

        self.set_ready()

        # Location

        name = current.get(
            "name",
            "Unknown"
        )

        country = current.get(
            "sys",
            {}
        ).get(
            "country",
            ""
        )

        self.location_label.configure(
            text=f"{name}, {country}".strip(", ")
        )

        # Temperature

        symbol = (
            "°F"
            if self.units == "imperial"
            else "°C"
        )

        self.temperature_label.configure(
            text=f'{current["main"]["temp"]:.0f}{symbol}'
        )

        # Condition

        self.condition_label.configure(
            text=current["weather"][0]
            ["description"]
            .title()
        )

        # Updated

        self.updated_label.configure(
            text=datetime.now().strftime(
                "Updated %d %b %Y • %H:%M"
            )
        )

        # Metrics

        self.metric_values["feels"].configure(
            text=f'{current["main"]["feels_like"]:.0f}{symbol}'
        )

        self.metric_values["humidity"].configure(
            text=f'{current["main"]["humidity"]}%'
        )

        wind_unit = (
            "mph"
            if self.units == "imperial"
            else "m/s"
        )

        self.metric_values["wind"].configure(
            text=f'{current.get("wind", {}).get("speed", 0):.1f} {wind_unit}'
        )

        self.metric_values["pressure"].configure(
            text=f'{current["main"].get("pressure", 0)} hPa'
        )

        self.metric_values["visibility"].configure(
            text=f'{current.get("visibility", 0) / 1000:.1f} km'
        )

        self.metric_values["clouds"].configure(
            text=f'{current.get("clouds", {}).get("all", 0)}%'
        )

        self.metric_values["sunrise"].configure(
            text=self.format_time(
                current.get("sys", {}).get("sunrise")
            )
        )

        self.metric_values["sunset"].configure(
            text=self.format_time(
                current.get("sys", {}).get("sunset")
            )
        )

        # Current weather icon

        self.load_icon(
            current["weather"][0]["icon"],
            self.weather_icon,
            110
        )

        # Forecasts

        self.render_hourly(
            forecast
        )

        self.render_daily(
            forecast
        )

        # Search history

        if (
            not self.use_location
            and self.last_query
        ):

            self.update_history(
                self.last_query
            )

    # =====================================================
    # HOURLY FORECAST
    # =====================================================

    def render_hourly(
        self,
        forecast
    ):

        for widget in \
                self.hourly_frame.winfo_children():

            widget.destroy()

        items = forecast.get(
            "list",
            []
        )[:3]

        for column in range(3):

            self.hourly_frame \
                .grid_columnconfigure(
                    column,
                    weight=1
                )

        symbol = (
            "°F"
            if self.units == "imperial"
            else "°C"
        )

        for index, item in \
                enumerate(items):

            card = ctk.CTkFrame(
                self.hourly_frame,
                corner_radius=15
            )

            card.grid(
                row=0,
                column=index,
                padx=5,
                pady=5,
                sticky="ew"
            )

            time = datetime.fromtimestamp(
                item["dt"]
            ).strftime(
                "%a • %H:%M"
            )

            ctk.CTkLabel(
                card,
                text=time,
                font=ctk.CTkFont(
                    size=15,
                    weight="bold"
                )
            ).pack(
                pady=(13, 3)
            )

            icon = ctk.CTkLabel(
                card,
                text="☁",
                font=ctk.CTkFont(
                    size=35
                )
            )

            icon.pack()

            self.load_icon(
                item["weather"][0]["icon"],
                icon,
                60
            )

            ctk.CTkLabel(
                card,
                text=f'{item["main"]["temp"]:.0f}{symbol}',
                font=ctk.CTkFont(
                    size=24,
                    weight="bold"
                )
            ).pack()

            ctk.CTkLabel(
                card,
                text=item["weather"][0]
                ["description"]
                .title()
            ).pack(
                pady=(2, 14)
            )

    # =====================================================
    # DAILY FORECAST
    # =====================================================

    def render_daily(
        self,
        forecast
    ):

        for widget in \
                self.daily_frame.winfo_children():

            widget.destroy()

        grouped = {}

        for item in forecast.get(
            "list",
            []
        ):

            day = datetime.fromtimestamp(
                item["dt"]
            ).date()

            grouped.setdefault(
                day,
                []
            ).append(item)

        days = list(
            grouped.items()
        )[:5]

        for column in range(5):

            self.daily_frame \
                .grid_columnconfigure(
                    column,
                    weight=1
                )

        for index, (
            day,
            items
        ) in enumerate(days):

            card = ctk.CTkFrame(
                self.daily_frame,
                corner_radius=15
            )

            card.grid(
                row=0,
                column=index,
                padx=4,
                pady=5,
                sticky="ew"
            )

            representative = min(
                items,
                key=lambda x:
                abs(
                    datetime.fromtimestamp(
                        x["dt"]
                    ).hour - 12
                )
            )

            high = max(
                x["main"]["temp_max"]
                for x in items
            )

            low = min(
                x["main"]["temp_min"]
                for x in items
            )

            ctk.CTkLabel(
                card,
                text=day.strftime("%a"),
                font=ctk.CTkFont(
                    size=16,
                    weight="bold"
                )
            ).pack(
                pady=(12, 0)
            )

            ctk.CTkLabel(
                card,
                text=day.strftime("%d %b")
            ).pack()

            icon = ctk.CTkLabel(
                card,
                text="☁"
            )

            icon.pack()

            self.load_icon(
                representative["weather"]
                [0]["icon"],
                icon,
                55
            )

            ctk.CTkLabel(
                card,
                text=f"{high:.0f}° / {low:.0f}°",
                font=ctk.CTkFont(
                    size=17,
                    weight="bold"
                )
            ).pack()

            ctk.CTkLabel(
                card,
                text=representative[
                    "weather"
                ][0]["description"].title(),
                wraplength=125
            ).pack(
                pady=(2, 12)
            )

    # =====================================================
    # WEATHER ICON
    # =====================================================

    def load_icon(
        self,
        code,
        label,
        size
    ):

        def worker():

            try:

                url = (
                    "https://openweathermap.org/"
                    "img/wn/"
                    f"{code}@2x.png"
                )

                with urllib.request.urlopen(
                    url,
                    timeout=6
                ) as response:

                    image = Image.open(
                        BytesIO(
                            response.read()
                        )
                    ).convert(
                        "RGBA"
                    )

                image.thumbnail(
                    (size, size)
                )

                photo = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=image.size
                )

                self.after(
                    0,
                    lambda:
                    label.configure(
                        image=photo,
                        text=""
                    )
                )

                label.image = photo

            except Exception:

                pass

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def format_time(timestamp):

        if not timestamp:

            return "--"

        return datetime.fromtimestamp(
            timestamp
        ).strftime(
            "%H:%M"
        )

    def set_ready(self):

        self.loading = False

        self.search_button.configure(
            state="normal"
        )

        self.location_button.configure(
            state="normal"
        )

        self.refresh_button.configure(
            state="normal"
        )

        self.status.configure(
            text=f"● Updated "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )

    def show_error(
        self,
        message
    ):

        self.loading = False

        self.search_button.configure(
            state="normal"
        )

        self.location_button.configure(
            state="normal"
        )

        self.refresh_button.configure(
            state="normal"
        )

        self.status.configure(
            text=f"⚠ {message}"
        )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app = WeatherApp()

    app.mainloop()
