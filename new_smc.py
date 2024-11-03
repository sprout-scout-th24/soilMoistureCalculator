import RPi.GPIO as GPIO
from flask import Flask, jsonify
from flask_cors import CORS  # Allow CORS if needed
import time
import threading
from datetime import datetime

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

MOISTURE_PIN = 23 

# Set up the GPIO pin as an input
GPIO.setup(MOISTURE_PIN, GPIO.IN)

app = Flask(__name__)
CORS(app)  # Enable CORS if your app runs in a web environment

last_moisture_status = "Unknown"
last_transition_time = None

def monitor_moisture():
    global last_moisture_status, last_transition_time
    while True:
        current_status = "Dry soil detected!" if GPIO.input(MOISTURE_PIN) else "Moist soil detected!"
       
        # Check if the status has changed
        if current_status != last_moisture_status:
            # Update the last transition time and status
            last_moisture_status = current_status
            last_transition_time = datetime.now()
            print(f"Status changed to: {last_moisture_status} at {last_transition_time}")

        time.sleep(1)

# Start the monitoring in a background thread
threading.Thread(target=monitor_moisture, daemon=True).start()

@app.route('/moisture', methods=['GET'])
def get_moisture():
    # Format the transition time if it exists
    transition_time = last_transition_time.strftime('%Y-%m-%d %H:%M:%S') if last_transition_time else "No transition detected yet"
   
    print(f"Moisture Status: {last_moisture_status} at {transition_time}")

    return jsonify({
        'moisture_status': last_moisture_status,
        'last_transition_time': transition_time
    })

if __name__ == '__main__':
    try:
        print("Starting the Flask server...")
        app.run(host='0.0.0.0', port=5000)  # Make it accessible over the network
    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        GPIO.cleanup()  # Clean up the GPIO setup
