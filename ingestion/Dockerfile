FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN cat emumba_ingestion/utils/updated_pptx_base.py > /usr/local/lib/python3.10/site-packages/llama_index/readers/file/slides/base.py

CMD ["python", "main.py"]