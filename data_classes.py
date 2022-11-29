from pydantic import BaseModel


class WeatherDetail(BaseModel):
    """Модель погодных условий: температура и осадки за час."""

    hour: str
    temp: int
    condition: str


class Weather(BaseModel):
    """Модель описывающая погоду на дату."""

    date: str
    hours: list[WeatherDetail]


class Forecast(BaseModel):
    """Модель описывающая прогноз погоды на список дат."""

    forecasts: list[Weather]
