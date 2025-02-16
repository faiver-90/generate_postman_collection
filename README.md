# 🚀 Postman Collection Generator (Dockerized)

Этот проект автоматически загружает OpenAPI спецификацию, формирует коллекцию **Postman** и загружает её в указанное рабочее пространство.

## 📦 Установка
### 1. Клонирование репозитория
```sh
git clone https://github.com/your-repository/postman-collection-generator.git
cd postman-collection-generator
```

### 2. Создание `.env` файла
Создайте файл `.env` в корневой папке и добавьте:
```
POSTMAN_KEY=your_postman_api_key
POSTMAN_WORKSPACE_ID=your_workspace_id
OPENAPI_URL=http://host.docker.internal:8080/api/openapi.json
```

## 🚀 Запуск через Docker
Скрипт **автоматически проверяет**, собран ли образ. Если нет — собирает, если уже есть — просто запускает контейнер.

### 🏗 **Сборка и запуск контейнера**
```sh
run_docker.bat
```

## 🔧 Ручная сборка и запуск (если нужно)
Если хотите собрать и запустить контейнер вручную:
```sh
# Собрать образ
docker build -t postman_collector .

# Запустить контейнер
docker run --rm --env-file .env postman_collector
```

## 🛠 Что делает этот проект?
1. **Загружает OpenAPI спецификацию** из указанного URL.
2. **Создаёт Postman-коллекцию**, разделяя эндпоинты по тегам.
3. **Генерирует тело запроса** по схеме OpenAPI.
4. **Загружает коллекцию в Postman** (с названием `Cryptouch_YYYY-MM-DD_HH-MM-SS`).
5. **Работает в Docker**.

✅ **Теперь можно быстро импортировать API-коллекцию в Postman и тестировать!** 🚀

