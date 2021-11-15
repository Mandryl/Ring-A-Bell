FROM registry.access.redhat.com/ubi8/python-39

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src
COPY ./all-mpnet-base-v2 /app/all-mpnet-base-v2

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
