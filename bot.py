import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
import speech_recognition as sr
from pydub import AudioSegment

from config import BOT_TOKEN
from utils import get_weather, get_rates, translate, calc, convert_units
from db import init_db, save_log
from tts_util import tts

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

init_db()

@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer(
        "🤖 Бот-справочник.\n"
        "/weather <город>\n"
        "/rates <валюта>\n"
        "/translate <слово>\n"
        "/calc <пример>\n"
        "/convert <выражение>\n"
        "Можно присылать голосовые!"
    )


# ================================
#        ТЕКСТОВЫЕ КОМАНДЫ
# ================================

@dp.message(Command("weather"))
async def weather_cmd(msg: Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Использование: /weather <город>")
        return
    city = parts[1]
    ans = get_weather(city)
    save_log("weather", city, ans)
    await msg.answer(ans)


@dp.message(Command("rates"))
async def rates_cmd(msg: Message):
    parts = msg.text.split(maxsplit=1)
    base = parts[1] if len(parts) > 1 else "USD"
    ans = get_rates(base)
    save_log("rates", base, ans)
    await msg.answer(ans)


@dp.message(Command("translate"))
async def translate_cmd(msg: Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Использование: /translate <слово>")
        return
    txt = parts[1]
    ans = translate(txt)
    save_log("translate", txt, ans)
    await msg.answer(ans)


@dp.message(Command("calc"))
async def calc_cmd(msg: Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Использование: /calc <пример>")
        return
    expr = parts[1]
    ans = calc(expr)
    save_log("calc", expr, ans)
    await msg.answer(f"Ответ: {ans}")


@dp.message(Command("convert"))
async def convert_cmd(msg: Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Использование: /convert <выражение>")
        return
    expr = parts[1]
    ans = convert_units(expr)
    save_log("convert", expr, ans)
    await msg.answer(ans)


@dp.message(Command("say"))
async def tts_cmd(msg: Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Использование: /say <текст>")
        return
    text = parts[1]

    file = tts(text)
    await msg.answer_voice(FSInputFile(file))
    save_log("tts", text, "[audio]")
    os.remove(file)


# ================================
#         ГОЛОСОВЫЕ КОМАНДЫ
# ================================

@dp.message(F.voice)
async def voice_handler(msg: Message):
    file = await bot.get_file(msg.voice.file_id)
    data = await bot.download_file(file.file_path)

    with open("voice.ogg", "wb") as f:
        f.write(data.read())

    # OGG → WAV
    try:
        audio = AudioSegment.from_ogg("voice.ogg")
        audio.export("voice.wav", format="wav")
    except Exception:
        await msg.answer("Ошибка конвертации аудио")
        return

    r = sr.Recognizer()
    try:
        with sr.AudioFile("voice.wav") as src:
            audio = r.record(src)
        text = r.recognize_google(audio, language="ru-RU")
    except Exception:
        text = "[не распознано]"

    save_log("voice", "[voice message]", text)
    await msg.answer(f"Распознано: {text}")

    # Удаляем файлы
    try:
        os.remove("voice.ogg")
        os.remove("voice.wav")
    except:
        pass

    # === Авто-выполнение голосовых команд ===
    t = text.lower()

    if t.startswith("погода"):
        city = t.replace("погода", "").strip()
        if city:
            ans = get_weather(city)
            await msg.answer(ans)
        return

    if t.startswith("курс"):
        parts = t.split()
        base = parts[1] if len(parts) > 1 else "USD"
        ans = get_rates(base)
        await msg.answer(ans)
        return

    if t.startswith("переведи"):
        word = t.replace("переведи", "").strip()
        ans = translate(word)
        await msg.answer(ans)
        return

    if any(x in t for x in "+-*/"):
        try:
            result = calc(t)
            await msg.answer(f"Ответ: {result}")
        except:
            await msg.answer("Ошибка в выражении")
        return


# ================================
#          СТАРТ БОТА
# ================================

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())