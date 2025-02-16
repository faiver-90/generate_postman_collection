@echo off
SET CONTAINER_NAME=postman_collection_generator
SET IMAGE_NAME=postman_collector

:: Проверяем, запущен ли контейнер
docker ps -a --format "{{.Names}}" | findstr /C:"%CONTAINER_NAME%" > nul
IF %ERRORLEVEL% == 0 (
    echo Контейнер уже существует. Запуск...
    docker start %CONTAINER_NAME%
) ELSE (
    echo Контейнер не найден. Собираем и запускаем...
    docker build -t %IMAGE_NAME% .
    docker run --name %CONTAINER_NAME% --env-file .env %IMAGE_NAME%
)

:: Проверка логов при необходимости
docker logs -f %CONTAINER_NAME%
