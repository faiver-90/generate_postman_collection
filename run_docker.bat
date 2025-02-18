@echo off
SET CONTAINER_NAME=postman_collection_generator
SET IMAGE_NAME=postman_collector

:: Проверяем, существует ли образ
docker images -q %IMAGE_NAME% > nul
IF %ERRORLEVEL% NEQ 0 (
    echo Образ не найден. Собираем...
    docker build -t %IMAGE_NAME% .
) ELSE (
    echo Образ найден. Создаём новый...
    docker rmi -f %IMAGE_NAME%
    docker build -t %IMAGE_NAME% .
)

echo Запуск контейнера...
docker run --rm --env-file .env %IMAGE_NAME%

echo Контейнер успешно завершил работу и был удален.