#!/usr/bin/env python3
import time
import json
import paho.mqtt.publish as publish
from solmate_sdk import SolMateAPIClient

# Configuration constants – adjust these as needed.
SOLMATE_SERIAL = "S2K0810A00002416"  # Replace with your SolMate serial number
SOLMATE_PASSWORD = "NgeggDtaGC"       # Replace with your SolMate password, if needed
MQTT_TOPIC = "home/solmate"
MQTT_HOST = "localhost"               # Change if your MQTT broker is hosted elsewhere
POLL_INTERVAL = 60                    # Seconds

# If your MQTT broker requires authentication, update these credentials.
mqtt_auth = {"username": "your_mqtt_username", "password": "your_mqtt_password"}
# If not needed, you can set mqtt_auth to None or remove the auth parameter in publish.single().

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
            # Publish a JSON payload to the MQTT topic.
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
