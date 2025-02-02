FROM python:3.11-slim

# Install required Python packages.
RUN pip install solmate-sdk paho-mqtt

# Copy the integration script into the container.
COPY solmate_mqtt.py /app/solmate_mqtt.py

WORKDIR /app

# The script should run continuously.
CMD ["python", "solmate_mqtt.py"]
