FROM python:3.12

WORKDIR /app

COPY .env .

COPY requirements.txt .

COPY . . 

RUN pip install -r requirements.txt

EXPOSE 8000

RUN python manage.py makemigrations

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
