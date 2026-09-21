FROM python:3.10-slim

# Установка системных зависимостей (ffmpeg для работы с голосовыми и видеосообщениями)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Отключение буферизации вывода для корректного отображения логов в Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода бота
COPY bot.py .

CMD ["python", "bot.py"]
