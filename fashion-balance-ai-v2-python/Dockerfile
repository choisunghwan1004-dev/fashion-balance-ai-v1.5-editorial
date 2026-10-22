FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py auth.py db.py recommend.py vision.py run.py migrate_photos.py mobile_setup.py ./
COPY frontend/dist ./frontend/dist
COPY public/images ./public/images
RUN useradd --create-home fashion && mkdir -p private/uploads && chown -R fashion:fashion /app
USER fashion
EXPOSE 3000
CMD ["python", "run.py"]
