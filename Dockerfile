FROM python:3.8

LABEL maintainer="Ngoc Trinh"

COPY ./techtrends /app

WORKDIR /app

RUN pip install -r requirements.txt && python init_db.py

EXPOSE 3111

CMD ["python", "app.py"]

