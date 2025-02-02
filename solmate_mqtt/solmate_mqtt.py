#!/usr/bin/env python3
import os
import time
import json
import paho.mqtt.publish as publish
from solmate_sdk import SolMateAPIClient

# Read configuration from environment variables
SOLMATE_SERIAL = os.getenv("solmate_serial")
SOLMATE_PASSWORD = os.getenv("solmate_password")
MQTT_TOPIC = os.getenv("mqtt_topic", "home/solmate")
MQTT_HOST = os.getenv("mqtt_host", "localhost")
POLL_INTERVAL = int(os.getenv("poll_interval", "60"))

# Read MQTT authentication credentials
MQTT_USERNAME = os.getenv("mqtt_username")
MQTT_PASSWORD = os.getenv("mqtt_password")
mqtt_auth = {"username": MQTT_USERNAME, "password": MQTT_PASSWORD} if MQTT_USERNAME and MQTT_PASSWORD else None

def main():
    client = SolMateAPIClient(SOLMATE_SERIAL)
    try:
        client.connect()
        if SOLMATE_PASSWORD:
            client.quickstart(password=SOLMATE_PASSWORD)
        else:
            client.quickstart()
        print("SolMate quickstart completed successfully.")
    except Exception as e:
        print("Error initializing SolMate client:", e)
        return

    while True:
        try:
            online_status = client.check_online()
            live_values = client.get_live_values()
            print(f"Online: {online_status}, Live values: {live_values}")
            payload = json.dumps({
                "online": online_status,
                "values": live_values
            })
            publish.single(MQTT_TOPIC, payload, hostname=MQTT_HOST, auth=mqtt_auth)
        except Exception as ex:
            print("Error updating SolMate data:", ex)
            error_message = str(ex).lower()
            if "1011" in error_message or "keepalive" in error_message:
                print("Detected keepalive ping timeout error. Attempting reconnection...")
                try:
                    client.connect()
                    if SOLMATE_PASSWORD:
                        client.quickstart(password=SOLMATE_PASSWORD)
                    else:
                        client.quickstart()
                    print("Reconnected successfully.")
                except Exception as recon_ex:
                    print("Reconnection attempt failed:", recon_ex)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
