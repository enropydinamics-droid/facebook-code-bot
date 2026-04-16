FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Объявляем аргументы (их значения будут подставлены из Railway Variables)
ARG TELEGRAM_TOKEN
ARG RAPIDAPI_KEY
ARG RAPIDAPI_HOST

# Превращаем аргументы в переменные окружения
ENV TELEGRAM_TOKEN=$TELEGRAM_TOKEN
ENV RAPIDAPI_KEY=$RAPIDAPI_KEY
ENV RAPIDAPI_HOST=$RAPIDAPI_HOST

CMD ["python", "bot.py"]