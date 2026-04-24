FROM python:3.12-slim

WORKDIR /app

# Kopiuj shared (protokół komunikacji) — context = distributed/
COPY shared/ /app/shared/

# Kopiuj moduły koordynatora
COPY coordinator/graph_loader.py /app/graph_loader.py
COPY coordinator/component_detector.py /app/component_detector.py
COPY coordinator/coordinator.py /app/coordinator.py

CMD ["python", "-u", "coordinator.py"]
