#!/usr/bin/env python3

import logging
import time
import subprocess
import psutil
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from smbus import SMBus
from bme280 import BME280
from ltr559 import LTR559
from enviroplus import gas
from rq import Queue
from rq.job import Job
from worker import conn
from display_worker import display
from devicesPython import mic
from datetime import datetime
import multiprocessing
import ssl
import requests
app = Flask(__name__)
CORS(app)  # Activate CORS on the app
app.config['CORS_HEADERS'] = 'Content-Type' # Set CORS headers
#see https://flask-cors.readthedocs.io/en/v1.7.4/
#https :
sslContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
sslContext.load_cert_chain('raspberrypi-fr.local.crt', 'raspberrypi-fr.local.key', "3153")
# Initialize sensors
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)
ltr559 = LTR559()

# Sensor configurations
temperature_oversampling = 2
pressure_oversampling = 16
humidity_oversampling = 1
t_measurement_normal = 1 + (2 * temperature_oversampling) + (2 * pressure_oversampling + 0.5) + (2 * humidity_oversampling + 0.5)
t_standby = 0.5
freq_bme280 = 1000 / (t_measurement_normal + t_standby)
bme280.setup(
    temperature_standby=t_standby,
    temperature_oversampling=temperature_oversampling,
    pressure_oversampling=pressure_oversampling,
    humidity_oversampling=humidity_oversampling
)
#mic :
mic = mic.Mic()
# Redis Queue setup
q = Queue(connection=conn)

def is_python_script_running(script_name):
    for process in psutil.process_iter(['cmdline']):
        try:
            cmdline = process.info['cmdline']
            if len(cmdline) > 1 and cmdline[0] == "python3" and script_name in cmdline[1]:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def start_python_script(script_path):
    if not is_python_script_running(script_path):
        subprocess.Popen(["python3", script_path])
def get_qnh(airport_code):
    url = f"https://www.aviationweather.gov/metar/data?ids={airport_code}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]["altimeter"]
@app.route('/temperature', methods=['GET'])
def get_temperature():
    temperature = round(bme280.get_temperature())
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    app.logger.info(f"Measurement info - normal: {t_measurement_normal}, standby: {t_standby}, frequency: {freq_bme280} Hz")
    return jsonify({'value': temperature, 'timestamp': timestamp, 'frequency': freq_bme280, 'unit': '°C'})

@app.route('/pressure', methods=['GET'])
def get_pressure():
    pressure = round(bme280.get_pressure())
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({'value': pressure, 'timestamp': timestamp, 'frequency': freq_bme280, 'unit': 'hPa'})
@app.route('/altitude', methods=['GET'])
def get_altitude():
    #get qnh :

    qnh = get_qnh("LFPR")
    altitude = round(bme280.get_altitude(qnh))
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({'value': altitude, 'timestamp': timestamp, 'frequency': freq_bme280, 'unit': 'm'})
@app.route('/humidity', methods=['GET'])
def get_humidity():
    humidity = round(bme280.get_humidity())
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({'value': humidity, 'timestamp': timestamp, 'frequency': freq_bme280, 'unit': '%'})

@app.route('/light', methods=['GET'])
def get_light():
    lux = round(ltr559.get_lux())
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    frequency = 20  # ALS_MEAS_RATE=50ms
    return jsonify({'value': lux, 'timestamp': timestamp, 'frequency': frequency, 'unit': 'lux'})
@app.route("/proximity", methods=['GET'])
def get_proximity():
    proximity = ltr559.get_proximity()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    frequency = 20
    return jsonify({'value': proximity, 'timestamp': timestamp, 'frequency': frequency, 'unit': 'proximity'})
@app.route('/gas', methods=['GET'])
def get_gas():
    reading = gas.read_all()
    gas_oxidising = reading.oxidising
    gas_reducing = reading.reducing
    gas_nh3 = reading.nh3
    app.logger.debug(f"Gas data: {gas_oxidising}, {gas_reducing}, {gas_nh3}")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({'oxidising': f"{gas_oxidising:05.02f}", 'reducing': f"{gas_reducing:05.02f}", 'nh3': f"{gas_nh3:05.02f}", 'timestamp': timestamp, "unit":"Ω"})

@app.route('/display', methods=['POST'])
def display_data():
    data = request.json
    app.logger.info(f"Display request: {data}")
    job = q.enqueue(display, args=(data,))
    return jsonify({'job_id': job.id})

@app.route("/structure", methods=['GET'])
def get_structure():
    with open("structure_api.json", "r") as f:
        return jsonify(f.read())

@app.route("/job/<job_id>", methods=['GET'])
def get_job_status(job_id):
    try:
        job = Job.fetch(job_id, connection=conn)
        return jsonify({'job_id': job.id, 'status': job.get_status()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route("/recordings/<filename>", methods=['GET'])
def get_recording(filename):
    base = "/home/pi/Desktop/INTELLIJ/"
    try:
        with open(base+"recordings/"+filename, "rb") as f:
            return Response(f.read(), mimetype="audio/wav")
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#TODO : check for post / get and check for crash
@app.route("/mic/record", methods=['GET'])
def record_mic():
    # Create a filename with the current time
    filename = "recordings/recording" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".wav"
    base = "/home/pi/Desktop/INTELLIJ/"
    #launch worker to record the sound
    job = q.enqueue(mic.record_and_save, args=(5, base+filename,))
    return jsonify({'job_id': job.id, "filename": filename, "validity": "1800", "unit": "s"})
if __name__ == '__main__':
    # Start worker.py if not running
    if not is_python_script_running("worker.py"):
        print("worker.py not running, starting it")
        start_python_script("worker.py")
    else:
        print("worker.py already running")
        #kill the worker.py
        subprocess.Popen(["pkill", "-f", "worker.py"])
        while is_python_script_running("worker.py"):
            time.sleep(1)
        print("worker.py killed")
        print("Starting worker.py")
        start_python_script("worker.py")
    # Set debug mode to on
    #app.debug = True
    
    #launch the mic.cleanup func as  multiprocessing
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=mic.cleanup, args=(queue,))
    
    p.start()
    app.logger.setLevel(logging.DEBUG)

    # Run the Flask app
    app.run(host='0.0.0.0', port=8050, ssl_context=sslContext)
    #kill the worker.py and cleanup.py
    subprocess.Popen(["pkill", "-f", "worker.py"])

    
    print("worker.py and cleanup.py killed")
    queue.put('q')
    p.join()
