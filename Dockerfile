FROM python:3.8.19-slim-bullseye

COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8089

CMD ["python", "app.py"]

