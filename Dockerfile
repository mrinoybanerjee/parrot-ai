FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

ENV LLM_SERVER=http://host.docker.internal:8080

CMD ["streamlit", "run", "app.py"]