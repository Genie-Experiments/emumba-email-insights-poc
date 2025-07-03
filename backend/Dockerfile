FROM python:3.10.12

WORKDIR /emumba-rag-service

COPY requirements.txt /emumba-rag-service

RUN pip install --no-cache-dir -r requirements.txt

COPY . /emumba-rag-service

WORKDIR /emumba-rag-service/app

EXPOSE 5000

CMD ["python", "app.py"]
