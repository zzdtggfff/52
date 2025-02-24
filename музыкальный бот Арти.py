import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
import yt_dlp

# Укажите токен бота
BOT_TOKEN = "7791922420:AAF_Ov3uXsyxx8KsC6CJ8h5qN5w053khAJU"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Функция для поиска видео на YouTube
def search_youtube(query):
    ydl_opts = {
        "quiet": True,
        "default_search": "ytsearch",
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            return info["entries"][0]["webpage_url"], info["entries"][0]["title"]
        return None, None

# Функция для скачивания аудио
def download_audio(url):
    output_path = "downloads/%(title)s.%(ext)s"
    ydl_opts = {
        "outtmpl": output_path,
        "format": "bestaudio[ext=m4a]",
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        return None

# Функция для скачивания всех треков из плейлиста
def download_playlist(url):
    output_path = "downloads/%(playlist)s/%(title)s.%(ext)s"
    ydl_opts = {
        "outtmpl": output_path,
        "format": "bestaudio[ext=m4a]",
        "yesplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return [ydl.prepare_filename(entry) for entry in info["entries"]]
    except Exception as e:
        return None

# Команда /start
@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.reply("Привет! Отправь название песни или ссылку на трек/плейлист с YouTube.")

# Обработка сообщений
@dp.message_handler()
async def process_message(message: Message):
    query = message.text.strip()

    if "youtube.com/playlist" in query or "youtu.be" in query and "list=" in query:
        await message.reply("Скачиваю плейлист, это может занять время...")
        audio_paths = download_playlist(query)
        if audio_paths:
            for audio_path in audio_paths:
                if os.path.exists(audio_path):
                    with open(audio_path, "rb") as audio:
                        await message.reply_audio(audio)
                    os.remove(audio_path)
        else:
            await message.reply("Ошибка при скачивании плейлиста.")
        return
    
    if "youtube.com" in query or "youtu.be" in query:
        await message.reply("Скачиваю аудио...")
        audio_path = download_audio(query)
        if audio_path and os.path.exists(audio_path):
            with open(audio_path, "rb") as audio:
                await message.reply_audio(audio)
            os.remove(audio_path)
        else:
            await message.reply("Ошибка при скачивании аудио.")
        return
    
    await message.reply("Ищу трек, пожалуйста, подождите...")
    video_url, title = search_youtube(query)
    if video_url:
        await process_message(types.Message(message_id=message.message_id, chat=message.chat, text=video_url))
    else:
        await message.reply("Не удалось найти трек. Отправьте ссылку на YouTube.")

# Запуск бота
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(dp.start_polling())
