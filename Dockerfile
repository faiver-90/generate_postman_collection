FROM python:3.9

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только необходимые файлы
COPY generate_postman_collection.py /app/
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Определяем команду запуска
CMD ["python", "/app/generate_postman_collection.py"]
