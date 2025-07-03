## Installation

1. **Clone the repository**:

   ```sh
   git clone https://github.com/yourusername/emumba-rag-service.git
   cd emumba-rag-service
   ```

2. **Create and activate a virtual environment**:

   ```sh
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. **Install the dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration

1. **Set up environment variables**:
   Create a [`.env`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2F.env%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/danial-emumba/Projects/emumba-POC/repos/emumba-rag-service/.env") file in the root directory and add the necessary environment variables:

   ```env
   AWS_S3_BUCKET=your_aws_s3_bucket
   EMBEDDING_URL=your_embedding_url
   EMBEDDING_MODEL=your_embedding_model
   OPENAI_API_BASE=your_openai_api_base
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=your_db_port
   LLM_MODEL=your_llm_model
   DB_NAME=your_db_name
   API_KEY=your_api_key
   SERVER_PORT=your_server_port
   ```

2. **Database Configuration**:
   The database configuration is managed in [`app/db/database.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fdb%2Fdatabase.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/danial-emumba/Projects/emumba-POC/repos/emumba-rag-service/app/db/database.py"). Ensure your database URL is correctly set in the [`.env`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2F.env%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/danial-emumba/Projects/emumba-POC/repos/emumba-rag-service/.env") file.

## Development

1. **Run the application**:

   ```sh
   uvicorn app.app:app --reload
   ```

2. **Access the API documentation**:
   Open your browser and navigate to [`http://127.0.0.1:8000/docs`](command:_github.copilot.openSymbolFromReferences?%5B%22http%3A%2F%2F127.0.0.1%3A8000%2Fdocs%22%2C%5B%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fservices%2Frag_service.py%22%2C%22external%22%3A%22file%3A%2F%2F%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fservices%2Frag_service.py%22%2C%22path%22%3A%22%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fservices%2Frag_service.py%22%2C%22scheme%22%3A%22file%22%7D%2C%22pos%22%3A%7B%22line%22%3A29%2C%22character%22%3A276%7D%7D%5D%5D "Go to definition") to access the interactive API documentation provided by FastAPI.

## Deployment

1. **Build the Docker image**:

   ```sh
   docker build -t emumba-rag-service .
   ```

2. **Run the Docker container**:

   ```sh
   docker run -d -p 5000:5000 --env-file .env emumba-rag-service
   ```

3. **Access the application**:
   Open your browser and navigate to [`http://127.0.0.1:5000`](command:_github.copilot.openSymbolFromReferences?%5B%22http%3A%2F%2F127.0.0.1%3A5000%22%2C%5B%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fservices%2Frag_service.py%22%2C%22external%22%3A%22file%3A%2F%2F%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fservices%2Frag_service.py%22%2C%22path%22%3A%22%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fservices%2Frag_service.py%22%2C%22scheme%22%3A%22file%22%7D%2C%22pos%22%3A%7B%22line%22%3A29%2C%22character%22%3A276%7D%7D%5D%5D "Go to definition") to access the deployed application.

## API Endpoints

- **Generate RAG Response**:
  - **Endpoint**: [`/generate`](command:_github.copilot.openSymbolFromReferences?%5B%22%2Fgenerate%22%2C%5B%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fapi%2Fv1%2Fendpoints%2Fquery.py%22%2C%22external%22%3A%22file%3A%2F%2F%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fapi%2Fv1%2Fendpoints%2Fquery.py%22%2C%22path%22%3A%22%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fapi%2Fv1%2Fendpoints%2Fquery.py%22%2C%22scheme%22%3A%22file%22%7D%2C%22pos%22%3A%7B%22line%22%3A11%2C%22character%22%3A19%7D%7D%5D%5D "Go to definition")
  - **Method**: `POST`
  - **Request Body**:
    ```json
    {
      "query": "Your main question",
      "company": "Company name",
      "sub_questions": [
        {
          "question": "Sub question 1",
          "tags": ["tag1", "tag2"]
        }
      ]
    }
    ```
  - **Response**:
    ```json
    {
        "response": "Generated response",
        "email_contributions": [...],
        "email_contributions_attachments": [...]
    }
    ```

## Logging

Logging is configured in [`app/config/LoggingConfig.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fconfig%2FLoggingConfig.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/danial-emumba/Projects/emumba-POC/repos/emumba-rag-service/app/config/LoggingConfig.py"). Logs are generated for various processing steps and errors.

## Middleware

Middleware for logging requests and measuring request times is defined in the [`app/middlewares`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Fdanial-emumba%2FProjects%2Femumba-POC%2Frepos%2Femumba-rag-service%2Fapp%2Fmiddlewares%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/danial-emumba/Projects/emumba-POC/repos/emumba-rag-service/app/middlewares") directory.

## Contributing

1. **Fork the repository**.
2. **Create a new branch**:
   ```sh
   git checkout -b feature-branch
   ```
3. **Make your changes**.
4. **Commit your changes**:
   ```sh
   git commit -m "Description of changes"
   ```
5. **Push to the branch**:
   ```sh
   git push origin feature-branch
   ```
6. **Create a pull request**.
