import os
import json
import requests
import time
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

POSTMAN_KEY = os.getenv("POSTMAN_KEY")
POSTMAN_WORKSPACE_ID = os.getenv("POSTMAN_WORKSPACE_ID")
OPENAPI_URL = os.getenv("OPENAPI_URL")


def fetch_openapi_spec(url):
    """Загружает OpenAPI спецификацию по URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def resolve_ref(ref, openapi_data):
    """Разворачивает ссылки $ref в OpenAPI"""
    ref_path = ref.lstrip("#/components/schemas/")
    return openapi_data.get("components", {}).get("schemas", {}).get(ref_path, {})


def extract_example(schema):
    """Извлекает пример из OpenAPI схемы или строит его на основе свойств"""
    if "example" in schema:
        return schema["example"]

    example = {}
    properties = schema.get("properties", {})
    for key, value in properties.items():
        example[key] = value.get("example", "string" if value.get("type") == "string" else 0)

    return example


def generate_postman_collection(openapi_data):
    """Генерирует Postman-коллекцию с группировкой по тегам и названием Cryptouch"""
    collection = {
        "info": {
            "name": "Cryptouch_" + time.strftime('%Y-%m-%d'),
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

                        example = extract_example(schema)

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
