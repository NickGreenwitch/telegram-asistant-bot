import requests
from googletrans import Translator
from simpleeval import simple_eval
from pint import UnitRegistry
import math

ureg = UnitRegistry()
translator = Translator()

# Погода (бесплатно)
def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=j1"
    r = requests.get(url, timeout=10)
    data = r.json()
    cur = data["current_condition"][0]
    desc = cur["weatherDesc"][0]["value"]
    temp = cur["temp_C"]
    feels = cur["FeelsLikeC"]
    humidity = cur["humidity"]
    wind = cur["windspeedKmph"]
    return f"🌤 Погода в {city}:\n{desc}, {temp}°C (ощущается {feels}°C)\n💧Влажность {humidity}%\n💨Ветер {wind} км/ч"

# Курс валют (бесплатно)
def get_rates(base="USD"):
    url = f"https://open.er-api.com/v6/latest/{base.upper()}"
    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        return "Ошибка: API валют недоступно."

    data = r.json()

    if data.get("result") != "success":
        return f"Ошибка: валюта {base} не найдена."

    rates = data["rates"]

    text = f"💱 Курсы валют (база {base.upper()}):\n"

    # первые 10 валют
    for k, v in list(rates.items())[:10]:
        text += f"1 {base.upper()} = {v:.3f} {k}\n"

    return text

# Перевод слов
def translate(text: str, target="ru"):
    t = translator.translate(text, dest=target)
    return t.text

# Калькулятор
def calc(expr: str):
    return str(simple_eval(expr, names={"pi": math.pi, "e": math.e}))

# Конвертер величин
def convert_units(expr: str):
    # формат: "10 kg to lb"
    parts = expr.split()
    if "to" not in parts:
        return "Формат: <число> <единица> to <единица>"
    i = parts.index("to")
    qty = float(parts[0])
    src = parts[1]
    dst = parts[i + 1]
    q = qty * ureg(src)
    return str(q.to(dst))