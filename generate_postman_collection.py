import os
import json
import requests
import time
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

POSTMAN_KEY = os.getenv("POSTMAN_KEY")
POSTMAN_WORKSPACE_NAME = os.getenv("POSTMAN_WORKSPACE_NAME")
OPENAPI_URL = os.getenv("OPENAPI_URL")


def get_workspace_id():
    """Получает ID воркспейса по его имени"""
    url = "https://api.getpostman.com/workspaces"
    headers = {"X-Api-Key": POSTMAN_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    workspaces = response.json().get("workspaces", [])

    for ws in workspaces:
        if ws["name"] == POSTMAN_WORKSPACE_NAME:
            return ws["id"]

    raise ValueError(f"Workspace '{POSTMAN_WORKSPACE_NAME}' не найден!")


POSTMAN_WORKSPACE_ID = get_workspace_id()


def fetch_openapi_spec(url):
    """Загружает OpenAPI спецификацию по URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def resolve_ref(ref, openapi_data):
    """Разворачивает ссылки $ref в OpenAPI"""
    ref_path = ref.lstrip("#/components/schemas/")
    return openapi_data.get("components", {}).get("schemas", {}).get(ref_path, {})


def extract_example(schema, openapi_data):
    """
    Извлекает пример из OpenAPI схемы или строит его на основе свойств.
    """
    if "$ref" in schema:
        schema = resolve_ref(schema["$ref"], openapi_data)

    if "example" in schema:
        return schema["example"]
    #
    if "anyOf" in schema:
        for option in schema["anyOf"]:
            if option.get("format") == "binary" and option.get("type") == "string":
                return "binary_data"
            if option.get("type") == "string":
                return "example_string_1"
            if option.get("type") == "integer":
                return 42
            if option.get("type") == "boolean":
                return True
            if "example" in option:
                return option["example"]

    if schema.get("type") == "array":
        items_schema = schema.get("items", {})
        return [extract_example(items_schema, openapi_data)]

    if schema.get("type") == "object":
        example = {}
        properties = schema.get("properties", {})
        for key, value in properties.items():
            example[key] = extract_example(value, openapi_data)
        return example

    if schema.get("type") == "string":
        if schema.get("format") == "date-time":
            return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return "example_string_2"

    if schema.get("type") == "integer":
        return 1  # Меняем 0 на 1 для корректных значений ID

    if schema.get("type") == "boolean":
        return False  # Используем False вместо 0

    if schema.get("type") == "null" or schema.get("nullable"):
        return None  # Корректная обработка null-значений

    return None


def generate_postman_collection(openapi_data):
    """Генерирует Postman-коллекцию с группировкой по тегам и названием Cryptouch"""
    collection = {
        "info": {
            "name": "Cryptouch_" + time.strftime('%Y-%m-%d_%H-%M-%S'),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    grouped_endpoints = {}

    for path, methods in openapi_data.get("paths", {}).items():
        for method, details in methods.items():
            tag = details.get("tags", ["Без категории"])[0]

            if tag not in grouped_endpoints:
                grouped_endpoints[tag] = []

            request = {
                "name": details.get("summary", f"{method.upper()} {path}"),
                "request": {
                    "method": method.upper(),
                    "url": {
                        "raw": "{{baseUrl}}" + path,
                        "host": ["{{baseUrl}}"],
                        "path": path.strip("/").split("/")
                    }
                }
            }

            if "parameters" in details:
                request["request"]["url"]["query"] = [
                    {"key": param["name"], "value": "", "description": param.get("description", "")}
                    for param in details["parameters"] if param.get("in") == "query"
                ]

            if "requestBody" in details and "content" in details["requestBody"]:
                for content_type, content in details["requestBody"]["content"].items():
                    if "schema" in content:
                        schema = content["schema"]
                        if "$ref" in schema:
                            schema = resolve_ref(schema["$ref"], openapi_data)

                        example = extract_example(schema, openapi_data)

                        request["request"]["body"] = {
                            "mode": "raw",
                            "raw": json.dumps(example, indent=2),
                            "options": {"raw": {"language": "json"}}
                        }
                        request["request"]["header"] = [{"key": "Content-Type", "value": content_type}]

            grouped_endpoints[tag].append(request)

    for tag, endpoints in grouped_endpoints.items():
        collection["item"].append({"name": tag, "item": endpoints})

    return collection


def upload_to_postman(collection):
    """Загружает коллекцию в Postman в указанный воркспейс"""
    url = "https://api.getpostman.com/collections"
    headers = {
        "X-Api-Key": POSTMAN_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "collection": collection,
        "workspace": POSTMAN_WORKSPACE_ID
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    print("✅ Коллекция успешно загружена в Postman:", response.json()["collection"]["uid"])


def main():
    print("🔍 Загружаем OpenAPI спецификацию...")
    openapi_data = fetch_openapi_spec(OPENAPI_URL)

    print("🔧 Генерируем Postman-коллекцию...")
    collection = generate_postman_collection(openapi_data)

    print("📤 Отправляем в Postman...")
    upload_to_postman(collection)


if __name__ == "__main__":
    main()
