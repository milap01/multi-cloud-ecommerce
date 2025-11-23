# 2025H1030231P

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/

# ENV for Event Hubs connection string injected at runtime
# ENV EVENT_HUB_CONN_STR_RESULTS="Endpoint=sb://..."

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
