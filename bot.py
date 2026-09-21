import os
import sys
import time
import uuid
import shutil
import tempfile
import telebot
import speech_recognition as sr
from pydub import AudioSegment

# ВСТАВЬТЕ СЮДА ВАШ ТОКЕН ОТ @BotFather:
BOT_TOKEN = "8911324707:AAFhbfZHF0QEHSjD39eP3_awFsa9dyU7DAI"

if BOT_TOKEN == "ВАШ_ТОКЕН_ЗДЕСЬ" or ":" not in BOT_TOKEN:
    print("Ошибка: замените 'ВАШ_ТОКЕН_ЗДЕСЬ' в 11-й строке bot.py на настоящий токен от @BotFather!")
    sys.exit(1)

# Подтягиваем ffmpeg в PATH для pydub
system_user_path = os.environ.get("PATH", "")
extra_ffmpeg_path = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin"
)
if os.path.exists(extra_ffmpeg_path) and extra_ffmpeg_path not in system_user_path:
    os.environ["PATH"] = extra_ffmpeg_path + os.pathsep + system_user_path

ffmpeg_exe = shutil.which("ffmpeg")
if ffmpeg_exe:
    AudioSegment.converter = ffmpeg_exe

bot = telebot.TeleBot(BOT_TOKEN)


def transcribe_audio_file(file_path: str) -> str:
    """Конвертирует аудио/видео файл в WAV и распознает русскую речь."""
    wav_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.wav")
    try:
        sound = AudioSegment.from_file(file_path)
        # Оптимизируем под распознавание: моно, 16 кГц
        sound = sound.set_channels(1).set_frame_rate(16000)
        sound.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        return recognizer.recognize_google(audio_data, language="ru-RU")
    finally:
        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except OSError:
                pass


def safe_edit_text(chat_id: int, message_id: int, text: str, parse_mode: str = None):
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode=parse_mode)
    except Exception as e:
        print(f"Не удалось обновить сообщение: {e}")


def process_audio_or_video(message, is_video: bool = False):
    """Общий обработчик голосовых сообщений и кружочков."""
    media_name = "кружочек" if is_video else "голосовое сообщение"
    icon = "📹" if is_video else "🎤"

    try:
        bot.send_chat_action(message.chat.id, "typing")
        status_msg = bot.reply_to(
            message, f"⏳ {icon} Обрабатываю {media_name}, распознаю речь..."
        )
    except Exception as e:
        print(f"Не удалось отправить начальный статус: {e}")
        return

    temp_input_path = ""
    try:
        if is_video:
            file_id = message.video_note.file_id
            ext = ".mp4"
        else:
            file_id = message.voice.file_id
            ext = ".ogg"

        file_info = bot.get_file(file_id)
        downloaded_bytes = bot.download_file(file_info.file_path)

        temp_input_path = os.path.join(
            tempfile.gettempdir(), f"{uuid.uuid4().hex}{ext}"
        )
        with open(temp_input_path, "wb") as f:
            f.write(downloaded_bytes)

        recognized_text = transcribe_audio_file(temp_input_path)
        result_text = f"{icon} <b>Текст ({media_name}):</b>\n\n{recognized_text}"
        safe_edit_text(status_msg.chat.id, status_msg.message_id, result_text, parse_mode="HTML")
    except sr.UnknownValueError:
        safe_edit_text(
            status_msg.chat.id,
            status_msg.message_id,
            f"❌ Не удалось распознать речь в {media_name}. Возможно, запись слишком тихая или неразборчивая.",
        )
    except sr.RequestError as e:
        safe_edit_text(
            status_msg.chat.id,
            status_msg.message_id,
            f"⚠️ Ошибка сервиса распознавания Google: {e}",
        )
    except Exception as e:
        safe_edit_text(
            status_msg.chat.id,
            status_msg.message_id,
            f"⚠️ Ошибка при обработке: {e}",
        )
    finally:
        if temp_input_path and os.path.exists(temp_input_path):
            try:
                os.remove(temp_input_path)
            except OSError:
                pass


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        user_name = message.from_user.first_name or "друг"
        welcome_text = (
            f"Привет, {user_name}! 👋\n\n"
            "Я бот для расшифровки речи в текст:\n"
            "🎤 Отправь голосовое сообщение — я переведу его в текст\n"
            "📹 Отправь видеосообщение (кружочек) — я тоже расшифрую его в текст!"
        )
        bot.reply_to(message, welcome_text)
    except Exception as e:
        print(f"Ошибка при ответе на /start: {e}")


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    process_audio_or_video(message, is_video=False)


@bot.message_handler(content_types=['video_note'])
def handle_video_note(message):
    process_audio_or_video(message, is_video=True)


if __name__ == "__main__":
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=20)
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as err:
            print(f"Ошибка polling: {err}. Перезапуск через 3 секунды...")
            time.sleep(3)



