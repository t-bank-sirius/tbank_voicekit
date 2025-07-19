import aiohttp
import asyncio
import logging
import os
import uuid

from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from aiogram.enums import ContentType

API_TOKEN = '8168879501:AAGfRNmE9TPFiknT4qBNMs1hY8o0OmZfu3k'
FASTAPI_URL = 'http://127.0.0.1:8009'
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audios")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

os.makedirs(AUDIO_DIR, exist_ok=True)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Пришли текст или аудио — получишь озвучку!")

@dp.message(F.content_type == ContentType.TEXT)
async def handle_text(message: Message):
    text = message.text
    async with aiohttp.ClientSession() as session:
        payload = {"text": text}
        async with session.post(f"{FASTAPI_URL}/tts", json=payload) as resp:
            if resp.status == 200:
                audio = await resp.read()
                audio_name = f"{uuid.uuid4()}.mp3"
                audio_path = os.path.join(AUDIO_DIR, audio_name)
                with open(audio_path, "wb") as f:
                    f.write(audio)
                audio_file = FSInputFile(audio_path, filename=audio_name)
                await message.answer_voice(voice=audio_file, caption="Озвученный текст")
            else:
                await message.reply("Ошибка TTS 😞")

@dp.message(F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def handle_voice(message: Message):
    file_id = message.voice.file_id if message.voice else message.audio.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    src = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(src) as tg_resp:
            if tg_resp.status != 200:
                await message.reply("Не удалось скачать аудиофайл")
                return
            audio_bytes = await tg_resp.read()

        data = aiohttp.FormData()
        data.add_field("audio", audio_bytes, filename="audio.mp3", content_type="audio/mpeg")
        async with session.post(f"{FASTAPI_URL}/stt", data=data) as stt_resp:
            if stt_resp.status != 200:
                await message.reply("Ошибка расшифровки аудио 😞")
                return
            stt_json = await stt_resp.json()
            text = stt_json.get("text", "")

        if not text:
            await message.reply("Не удалось распознать речь.")
            return

        payload = {"text": text}
        async with session.post(f"{FASTAPI_URL}/tts", json=payload) as tts_resp:
            if tts_resp.status == 200:
                audio = await tts_resp.read()
                audio_name = f"{uuid.uuid4()}.mp3"
                audio_path = os.path.join(AUDIO_DIR, audio_name)
                with open(audio_path, "wb") as f:
                    f.write(audio)
                audio_file = FSInputFile(audio_path, filename=audio_name)
                await message.answer_voice(voice=audio_file,
                                          caption=f"Распознан текст:\n{text}", title=audio_name)
            else:
                await message.reply("Ошибка синтеза речи 😞")

if __name__ == "__main__":
    dp.run_polling(bot)
