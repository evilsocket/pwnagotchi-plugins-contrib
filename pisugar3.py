# Based on the original plugin by evilsocket: https://github.com/evilsocket/pwnagotchi/blob/master/pwnagotchi/plugins/default/ups_lite.py
#
# Information on PiSugar v3 register
#
# https://github.com/PiSugar/PiSugar/wiki/PiSugar-3-Series#i2c-datasheet
# (The information on "External power supply detection" is incorrect in my battery. For me, the 3rd bit indicates if it's charging)
#
#
import logging
import struct

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


# TODO: implement turning off at certain voltage with an option in config.yml. For now I don't see a reason for this (maybe just for fun) since it Can be configured in the web UI of the PiSugar
class UPS:
    PISUGAR_ADDR = 0x57
    CAPACITY_ADDR = 0x2A
    LOW_VOLTAGE_ADDR = 0x23
    HIGH_VOLTAGE_ADDR = 0x22
    POWER_ADDR = 0x02
    
    def __init__(self):
        # only import when the module is loaded and enabled
        import smbus
        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self._bus = smbus.SMBus(1)

    def voltage(self):
        #return voltage in mV
        try:
            high_dec = self._bus.read_byte_data(self.PISUGAR_ADDR, self.HIGH_VOLTAGE_ADDR)
            low_dec = self._bus.read_byte_data(self.PISUGAR_ADDR, self.LOW_VOLTAGE_ADDR)
            pack_low = struct.pack('>H',low_dec)
            pack_high = struct.pack('H',high_dec)
            voltage = int.from_bytes(pack_low,"big") | int.from_bytes(pack_high,"big")  
            return voltage
        except Excetpion as e:
            logging.error("[pisugar3] Error at UPS.voltage(). Battery not in use. {}".str(e))
            return 0

    def capacity(self):
        try:
            read = self._bus.read_byte_data(self.PISUGAR_ADDR, self.CAPACITY_ADDR)
            return read
        except Exception as e:
            logging.error("[pisugar3] Failed at UPS.capacity(). Battery not in use. {}"+str(e))
            return 0

    def charging(self):
        #the 3rd bit of the 0X02 address. 1=chargin; 0=not charging
        try:
            power_dec = self._bus.read_byte_data(self.PISUGAR_ADDR, self.POWER_ADDR)
            power_bin = bin(power_dec)
            is_charging = power_bin[4] #The position 0,1 contains '0b'
            return '+' if is_charging=='1' else '-'
        except Exception as e:
            logging.error("[pisugar3] Failed at UPS.charging(). Battery not in use. {}".format(str(e)))
            return '*'


class UPSLite(plugins.Plugin):
    __author__ = 'zitro.roberto@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will add battery percentage indicator for the PiSugar v3'

    def __init__(self):
        self.ups = None

    def on_loaded(self):
        logging.info("[pisugar3] Plugin successfully loaded")
        self.ups = UPS()

    def on_ui_setup(self, ui):
        ui.add_element('ups', LabeledValue(color=BLACK, label='PWR', value='-', position=(ui.width() / 2 + 15, 0),
                                           label_font=fonts.Bold, text_font=fonts.Medium))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('ups')

    def on_ui_update(self, ui):
        try:
            capacity = self.ups.capacity()
            charging = self.ups.charging()
            ui.set('ups', "{}{}%".format(charging, capacity))
        except Exception as e:
            logginf.error("[pisugar] Error at on_ui_update: {}".format(str(e)))