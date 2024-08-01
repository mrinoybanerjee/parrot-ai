FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

ENV BACKEND_SERVER=http://backend:8000

CMD ["streamlit", "run", "app.py"]