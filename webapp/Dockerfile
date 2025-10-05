FROM python:3.11-slim
WORKDIR /app
# copy only the webapp folder contents into /app
WORKDIR /app/webapp
COPY webapp/ /app/webapp
RUN pip install --no-cache-dir -r /app/webapp/requirements.txt
EXPOSE 5000
CMD ["python3", "app.py"]
