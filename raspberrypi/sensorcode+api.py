import sys
from datetime import datetime
from time import sleep, time
import RPi.GPIO as GPIO
import requests
import base64
from dotenv import dotenv_values


# Constants
TRIG = 23
ECHO = 24
DISTANCE_THRESHOLD = 120  # in cm


# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

count = 0


def measure_distance():
    """Measure the distance using the ultrasonic sensor."""
    GPIO.output(TRIG, False)
    sleep(0.5)

    GPIO.output(TRIG, True)
    sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time()

    pulse_end = time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time()

    pulse_duration = pulse_end - pulse_start
    distance = (
        pulse_duration * 17150
    )  # Speed of sound: 34300 cm/s divided by 2 (to and from object)
    return round(distance, 2)


# load the environment variables
env = dotenv_values(".env")
api_key = env["API_KEY"]

try:
    print("Starting ultrasonic monitoring. Press Ctrl+C to exit.")
    while True:
        distance = measure_distance()
        print(f"Measured Distance: {distance} cm")

        if distance < DISTANCE_THRESHOLD:
            count += 1
            timestamp = datetime.now()
            print(f"Object detected! Total Count: {count}")

            data = {"count": count, distance: distance}
            # convert the data to string
            data = str(data)
            # encode the data to base64
            data = base64.b64encode(data.encode()).decode()

            req_data = {
                "recorded_at": datetime.now(),
                "data": data,
                "sensor_key": api_key,
            }

            # Save data to the database using the API
            response = requests.post(
                "https://idp_api.arfff.dog/api/v1/data", json=req_data
            )

            sleep(1)  # Avoid rapid overcounting

except KeyboardInterrupt:
    print("\nCtrl-C pressed. Cleaning up GPIO and closing database connection.")
    GPIO.cleanup()
    print("Database connection closed. Exiting.")
    sys.exit(0)
