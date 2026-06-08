FROM python:3.12-slim

WORKDIR /app

COPY shared/ /app/shared/
COPY coordinator/graph_loader.py /app/graph_loader.py
COPY coordinator/component_detector.py /app/component_detector.py
COPY coordinator/coordinator.py /app/coordinator.py
COPY coordinator/profile_coordinator.py /app/profile_coordinator.py

CMD ["python", "-u", "coordinator.py"]
