# emumba Outlook Ingestion

This document provides step-by-step instructions for running the emumba Outlook Ingestion project successfully. Please follow each step carefully to ensure a smooth setup.

## Prerequisites

Before you begin, make sure you have the following:

- Access to the terminal with administrator privileges.

## Setup Instructions

### Step 1: Gain Administrator Privileges

Open your terminal and run the following command to switch to the root user:

```
sudo su
```

### Step 2: Create the .env File

Create a `.env` file in the root directory of your project with the following content:

```
OPENAI_API_BASE=your-openai-api-base
LLM_MODEL=your-llm-model
API_KEY=your-api-key
EMBEDDING_URL=your-embedding-url
EMBEDDING_MODEL=your-embedding-model
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_PORT=your-db-port
DB_NAME=your-db-name
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_S3_BUCKET=your-aws-s3-bucket
```

Replace the placeholders with actual values relevant to your project.

### Step 3: Build the Docker Image

Run the following command in your terminal to build the Docker image:

```
docker build -t emumba-outlook-ingestion .
```

### Step 4: Verify the Docker Image

After the build process completes, verify that the Docker image was created successfully by running:

```
docker images
```

You should see `emumba-outlook-ingestion` listed in the output.

### Step 5: Prepare Configuration Files

You need to create and provide two essential files: `config.yaml` and `customers.xlsx`.

#### 5.1 Create `config.yaml`

The `config.yaml` file should contain the following configurations:

```yaml
source:
  name: "ms_outlook"
  client_id: "your-client-id"
  tenant_id: "your-tenant-id"
  client_secret: "your-client-secret"
  scope: ["your-scope-or-default-scope"]
```

#### 5.1.1 Additional configuration

Additionally, the `config.yaml` file can include a failover section. This allows for restarting the script from a failure point. For example, if the script fails for a customer (e.g., Nike) during the email ingestion phase, you can rerun the container by adding a failover section in the `config.yaml` file:

```yaml
source:
  name: "ms_outlook"
  client_id: "your-client-id"
  tenant_id: "your-tenant-id"
  client_secret: "your-client-secret"
  scope: ["your-scope-or-default-scope"]
failover:
  customer: "Nike"
  type: "email"
```

The `type` field can have three values based on the ingestion stages: Email, Attachment, S3. If the script fails for a stage, you can restart the process by specifying the customer and the type to resume the process.

Make sure to replace the placeholders with actual values relevant to your project. Also, ensure that the file names are the same and the files are placed in the parent directory.

#### 5.2 Create `customers.xlsx`

The `customers.xlsx` file must follow this format:

```
Account Name | Account Owner Email | Solution Engineer Email
-----------------------------------------------------------
Nike         | abc@nike.com       | xyz@nike.com
PWC          | def@pwc.com        | def@pwc.com
```

Ensure that the first row contains headers, and each subsequent row contains customer data.

### Step 6: Run the Docker Container

To run the Docker container, use the following command:

```
docker run --env-file=./.env -v "$(pwd)/config.yaml:/home/config.yaml" -v "$(pwd)/customers.xlsx:/home/customers.xlsx" --name outlook-ingestion emumba-outlook-ingestion
```

### Optional Step: Run the Docker Container from Docker Hub

If you prefer to run the Docker container from the image pushed to Docker Hub, use the following command:

```
docker run -v "$(pwd)/config.yaml:/home/config.yaml" -v "$(pwd)/customers.xlsx:/home/customers.xlsx" --name outlook-ingestion ghcr.io/emumbaorg/emumba/emumba-outlook-ingestion:latest
```

This command will start a Docker container with the necessary configurations and data files mounted.

## Troubleshooting

If you encounter any issues, consider the following:

- Ensure Docker is running on your machine.
- Check that the file paths are correct and that both `config.yaml` and `customers.xlsx` are in your current working directory.
- Verify that you have the correct permissions for accessing these files.
