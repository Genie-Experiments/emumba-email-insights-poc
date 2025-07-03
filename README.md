# Emumba Email Insights POC

This project provides a comprehensive solution for processing and analyzing email and attachment data using AI-powered insights. It consists of three main components: a frontend web application, a backend RAG (Retrieval-Augmented Generation) service, and an email ingestion pipeline.

## 🎥 Demo Video

[Watch the demo video](https://drive.google.com/file/d/1Cu49Nuc4yV5AQ7zJKra8HJCS4n745Lvr/view) to see the application in action.

---

## Project Structure

This repository contains the following components:

- **`frontend/`** - React-based web application for user interface
- **`backend/`** - FastAPI-based RAG service for AI-powered insights
- **`ingestion/`** - Email data ingestion pipeline from Microsoft Outlook
- **`sample_s3_data/`** - Sample data and utilities for testing

---

## Quick Start (Docker Compose)

### Prerequisites

Ensure you have the following installed:

-   **Docker & Docker Compose**: For containerized services
-   **Python 3.x**: For running sample data scripts
-   **boto3**: AWS SDK for Python (`pip install boto3`)

### 1. Start Infrastructure Services

Start the required infrastructure services (PostgreSQL with pgvector and LocalStack for S3):

```bash
docker-compose up -d postgres localstack
```

### 2. Set Up LocalStack S3 Bucket

```bash
# Create the S3 bucket
docker exec -it localstack awslocal s3 mb s3://emumba-email-insights

# Verify bucket creation
docker exec -it localstack awslocal s3 ls
```

### 3. Load Sample Data (Optional)

If you don't have Outlook credentials, use sample data:

```bash
cd sample_s3_data

# Set AWS credentials in download_sample_data.py (contact the team for credentials)
python3 download_sample_data.py

# Insert sample data into LocalStack S3
python3 insert_sample_data_to_local_s3.py

# Verify data insertion
docker exec -it localstack awslocal s3 ls s3://emumba-email-insights/
```

### 4. Run Data Ingestion

```bash
# Configure environment variables in docker-compose.yml first
docker-compose up --build emumba-outlook-ingestion
```

**Note**: If ingestion fails due to Outlook connection issues, comment out the `ingest_outlook_to_s3(customers)` line in `ingestion/main.py`.

### 5. Start Application Services

```bash
# Start backend and frontend services
docker-compose up -d emumba-rag-service emumba-email-insights
```

### 6. Access the Application

Open your web browser and navigate to `http://localhost:5000` to access the web application.

---

## Component-Specific Setup

For detailed setup instructions for each component, please refer to their respective README files:

### Frontend
- **Location**: `frontend/README.md`
- **Description**: React + TypeScript web application with Vite
- **Development**: Instructions for local development, building, and deployment
- **Features**: Email insights interface, attachment viewing, AI query forms

### Backend
- **Location**: `backend/README.md`
- **Description**: FastAPI-based RAG service with PostgreSQL and vector search
- **Development**: API documentation, local development setup, and deployment
- **Features**: AI-powered email analysis, vector similarity search, response generation

### Ingestion
- **Location**: `ingestion/README.md`
- **Description**: Microsoft Outlook email ingestion pipeline
- **Setup**: Detailed configuration for Outlook API, customer data format, and failover handling
- **Features**: Automated email fetching, attachment processing, data storage

---

## Development Workflow

1. **Individual Component Development**: Each component can be developed independently using their respective README instructions
2. **Integration Testing**: Use Docker Compose for full-stack integration testing
3. **Production Deployment**: Follow the Docker-based deployment instructions in each component's README

---

## Troubleshooting

- **Container Issues**: Check `docker ps` to verify all containers are running
- **Database Access**: Use `docker exec -it postgres psql -U test -d test` to access PostgreSQL
- **S3 Storage**: Use `docker exec -it localstack awslocal s3 ls s3://emumba-email-insights/` to check S3 contents
- **Component-Specific Issues**: Refer to the individual README files in each component directory

---

## Configuration

Environment variables and configuration files are managed at the component level. See the respective README files for:

- **Frontend**: `frontend/README.md` - Build configuration, environment setup
- **Backend**: `backend/README.md` - API keys, database configuration, AI model settings  
- **Ingestion**: `ingestion/README.md` - Outlook API credentials, customer data format

