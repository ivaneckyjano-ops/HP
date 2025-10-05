FROM python:3.11-slim
WORKDIR /app
COPY webapp/ /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
# Use absolute path so the entrypoint reliably finds app.py regardless of WORKDIR changes
CMD ["python3", "/app/app.py"]
