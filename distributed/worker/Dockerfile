FROM python:3.12-slim

WORKDIR /app

# Kopiuj shared (protokół komunikacji) — context = distributed/
COPY shared/ /app/shared/

# Kopiuj workera
COPY worker/worker.py /app/worker.py

EXPOSE 5000

CMD ["python", "-u", "worker.py"]
