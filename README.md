# 🚀 Postman Collection Generator (Dockerized)

This project automatically fetches an OpenAPI specification, generates a **Postman** collection, and uploads it to the specified workspace.

## 📦 Installation
### 1. Clone the Repository
```sh
git clone https://github.com/your-repository/postman-collection-generator.git
cd postman-collection-generator
```

### 2. Create a `.env` File
Create a `.env` file in the root directory and add:
```
POSTMAN_KEY=your_postman_api_key
POSTMAN_WORKSPACE_ID=your_workspace_id
OPENAPI_URL=http://host.docker.internal:8080/api/openapi.json
POSTMAN_WORKSPACE_NAME=your_name_workspace
```

## 🚀 Running via Docker
The script **automatically checks** if the image is built. If not, it builds it; if the image exists, it simply runs the container.

### 🏗 **Build and Run the Container**
```sh
run_docker.bat
```

## 🔧 Manual Build and Run (if needed)
If you want to manually build and run the container:
```sh
# Build the image
docker build -t postman_collector .

# Run the container
docker run --rm --env-file .env postman_collector
```

## 🛠 What Does This Project Do?
1. **Fetches the OpenAPI specification** from the specified URL.
2. **Creates a Postman collection**, grouping endpoints by tags.
3. **Generates request bodies** based on the OpenAPI schema.
4. **Uploads the collection to Postman** (named `Cryptouch_YYYY-MM-DD_HH-MM-SS`).
5. **Runs inside Docker**.

✅ **Now you can quickly import the API collection into Postman and start testing!** 🚀