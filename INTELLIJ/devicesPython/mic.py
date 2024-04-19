import sounddevice as sd
import soundfile as sf
from datetime import datetime
import time
import redis
import os
import sys
import logging
from queue import Empty
from worker import conn
class Mic:
    def __init__(self):
        self.samplerate = 44100
        self.channels = 2
        self.chunk = 1024
        self.device = 0
        self.conn = redis.Redis()

    
    @classmethod
    def record_and_save(self, duration, filename):
        samplerate = 44100
        data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
        sd.wait()
        print(f"Recording finished. Saving to {filename}")
        print("data ", data)
        if data.size == (0,0):
            print("No data recorded.")
            return
        sf.write(filename, data, samplerate)
        
        
        # Save the filename and creation timestamp to Redis
        creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_info = {"url": filename, "timestamp": creation_time}
        conn.rpush('recordings', str(file_info))
    @classmethod
    def cleanup(self, queue):
        logging.basicConfig(level=logging.INFO, filename=f'logs/cleanup{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filemode='a')
        logging.info("Starting cleanup process...")
        while True:
            #get the list of recordings
            recordings = conn.lrange('recordings', 0, -1)
            logging.info(f"Recordings: {recordings}")
            #get the ones that are olders that 30min
            for recording in recordings:
                recording = eval(recording)
                logging.info(f"Recording: {recording}")
                timestamp = datetime.strptime(recording['timestamp'], "%Y-%m-%d %H:%M:%S")
                if (datetime.now() - timestamp).total_seconds() > 1800:# 30 minutes
                    #delete the file
                    logging.info(f"Deleting recording: {recording}")
                    conn.lrem('recordings', 0, str(recording))
                    #delete the file
                    try:
                        os.remove(recording['url'])
                    except Exception as e:
                        logging.error(f"Error deleting file: {e}")
            logging.info("Waiting for 30 seconds...")
            
            #test if we received q in stdin
            #if so, break the loop
            try:
                if queue.get(timeout=60*5) == 'q':
                    logging.info("Received q, breaking the loop...")
                    break
            except Empty:
                logging.info("No q received, continuing...")
            logging.info("Cleanup process finished.")
