FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dashboard dashboard
COPY src src
COPY data/processed data/processed
COPY reports reports
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/executive_app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
