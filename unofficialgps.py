from datetime import datetime 
import time 
import json 
import logging 
import os 
import serial 
import threading

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

class UnofficialGPS(plugins.Plugin):
    __author__ = "takenwiserix@gmail.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Save GPS coordinates whenever an handshake is captured. (same as official, but reading directly raw serial port - not using bettercap)"

    def __init__(self):
        self.running = False
        # We use same object as the initial bettercap gps module
        self.coordinates = {'Updated':datetime.utcnow().isoformat() + "Z",'Latitude':0,'Longitude':0,'FixQuality':0,'NumSatellites':0,'HDOP':0,'Altitude':0,'Separation':0}
        self.serialLock = threading.Lock()
        
    def on_loaded(self):
        logging.info(f"unofficial-gps plugin loaded for {self.options['device']}")

    def on_ready(self, agent):
        if os.path.exists(self.options["device"]):
            logging.info(
                f"enabling unofficial-gps module for {self.options['device']}"
            )
            self.serial  = serial.Serial(self.options['device'], baudrate = self.options['speed'], timeout = 0)
            self.running = True
            self.serialThread = threading.Thread(target=self.read_from_port)
            self.serialThread.start()
            logging.info('Serial Thread for unofficial-gps module started')
            
        else:
            logging.warning("no GPS detected")

    def read_from_port(self):
        while self.running:
           if (self.serial.inWaiting()>0):
               reading = self.serial.readline().decode()
               self.handle_serial_data(reading)
            
    def handle_serial_data(self, data):
        if len(data) >= 7:
            message = data[0:6]
            if (message == "$GPGGA"):
                parts = data.split(",")
                
                try:
                    # Get the position data that was transmitted with the GPRMC message
                    # refer to: http://aprs.gids.nl/nmea/#rmc
                    (format,
                    utc,
                    latitude, 
                    northsouth, 
                    longitude, 
                    eastwest, 
                    quality, 
                    number_of_satellites_in_use, 
                    horizontal_dilution, 
                    altitude, 
                    above_sea_unit, 
                    geoidal_separation, 
                    geoidal_separation_unit, 
                    data_age, 
                    diff_ref_stationID) = data.split(",")                  
                    quality=int(quality)
                    if quality > 0:
                        latitude_in=float(latitude)
                        longitude_in=float(longitude)
                        if northsouth == 'S':
                            latitude_in = -latitude_in
                        if eastwest == 'W':
                            longitude_in = -longitude_in
                        latitude_degrees = int(latitude_in/100)
                        latitude_minutes = latitude_in - latitude_degrees*100
                        
                        longitude_degrees = int(longitude_in/100)
                        longitude_minutes = longitude_in - longitude_degrees*100
                        
                        latitude = latitude_degrees + (latitude_minutes/60)
                        longitude = longitude_degrees + (longitude_minutes/60)
                        
                        timeOfFix = time.strftime("%H:%M:%S", time.strptime(utc.split(".")[0],"%H%M%S"))
                        altitude = float(altitude)
                    
                        with self.serialLock:
                            self.coordinates['Updated'] = datetime.utcnow().isoformat() + "Z"
                            self.coordinates['Longitude'] = longitude
                            self.coordinates['Latitude'] = latitude
                            self.coordinates['Altitude'] = altitude
                            self.coordinates['NumSatellites'] = number_of_satellites_in_use
                            self.coordinates['FixQuality'] = quality
                            self.coordinates['HDOP'] = float(horizontal_dilution)
                            self.coordinates['Separation'] = float(geoidal_separation)
                except Exception as ex:
                    logging.info(ex)
            else:
                # Handle other NMEA messages and unsupported strings
                pass
    
    def on_handshake(self, agent, filename, access_point, client_station):
        if self.running:
            info = agent.session()
            gps_filename = filename.replace(".pcap", ".gps.json")
            with self.serialLock:
                if self.coordinates and all([
                    # avoid 0.000... measurements
                    self.coordinates["Latitude"], self.coordinates["Longitude"]
                ]):
                    logging.info(f"saving GPS to {gps_filename} ({self.coordinates})")
                    with open(gps_filename, "w+t") as fp:
                        json.dump(self.coordinates, fp)
                else:
                    logging.info("not saving GPS. Couldn't find location.")

    def on_ui_setup(self, ui):
        # add coordinates for other displays
        if ui.is_waveshare_v2():
            lat_pos = (127, 75)
            lon_pos = (122, 84)
            alt_pos = (127, 94)
        elif ui.is_waveshare_v1():
            lat_pos = (130, 70)
            lon_pos = (125, 80)
            alt_pos = (130, 90)
        elif ui.is_inky():
            lat_pos = (127, 60)
            lon_pos = (127, 70)
            alt_pos = (127, 80)
        elif ui.is_waveshare144lcd():
            # guessed values, add tested ones if you can
            lat_pos = (67, 73)
            lon_pos = (62, 83)
            alt_pos = (67, 93)
        elif ui.is_dfrobot_v2: 
            lat_pos = (127, 75)
            lon_pos = (122, 84)
            alt_pos = (127, 94)
        elif ui.is_waveshare27inch():
            lat_pos = (6,120)
            lon_pos = (1,135)
            alt_pos = (6,150)
        else:
            # guessed values, add tested ones if you can
            lat_pos = (127, 51)
            lon_pos = (127, 56)
            alt_pos = (102, 71)

        label_spacing = 0

        ui.add_element(
            "latitude",
            LabeledValue(
                color=BLACK,
                label="lat:",
                value="-",
                position=lat_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=label_spacing,
            ),
        )
        ui.add_element(
            "longitude",
            LabeledValue(
                color=BLACK,
                label="long:",
                value="-",
                position=lon_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=label_spacing,
            ),
        )
        ui.add_element(
            "altitude",
            LabeledValue(
                color=BLACK,
                label="alt:",
                value="-",
                position=alt_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=label_spacing,
            ),
        )

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('latitude')
            ui.remove_element('longitude')
            ui.remove_element('altitude')

    def on_ui_update(self, ui):
        if self.coordinates and all([
            # avoid 0.000... measurements
            self.coordinates["Latitude"], self.coordinates["Longitude"]
        ]):
            with self.serialLock:
                ui.set("latitude", f"{self.coordinates['Latitude']:.4f} ")
                ui.set("longitude", f" {self.coordinates['Longitude']:.4f} ")
                ui.set("altitude", f" {self.coordinates['Altitude']:.1f}m ")
