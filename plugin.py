"""
<plugin key="Xiaomi_LYWSD03MMC" name="Xiaomi LYWSD03MMC" author="arnojdejong" version="1.0.0" >
    <description>
        <h2>Xiaomi LYWSD03MMC</h2><br/>
        Plugin to handle the bluetooth advertisement data of the Xiaomi LYWSD03MMC<br/>
        sensor needs custom firmware from https://github.com/atc1441/ATC_MiThermometer<br/>
    </description>
    <params>
        <param field="Mode1" label="Device selection" width="300px" required="true">
            <options>
                <option label="Automatic scanning" value="auto" default="true"/>
                <option label="Manual selection (add below)" value="manual"/>
            </options>
        </param>
        <param field="Mode2" label="Devices mac adresses, "aa:bb:cc:dd:ee:ff" and comma separated" width="300px" required="false" default=""/>

        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""
import asyncio

import Domoticz
import threading
import queue
import shelve
import time

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from XiaomiLYWSD03MMC import XiaomiLYWSD03MMC
from XiaomiLYWSD03MMC import XIAOMI_LYWSD03MMC_PROFILE_CUSTOM


class BasePlugin:
    def __init__(self):
        self.ble_queue = queue.Queue()
        self.message_queue = queue.Queue()
        self.message_thread = threading.Thread(name="QueueThread", target=BasePlugin.handle_message, args=(self,))
        self.ble_thread = threading.Thread(name="BleThread", target=BasePlugin.handle_ble, args=(self,))

        self.keeping_track = {}
        self.scanner = BleakScanner()
        self.scanner.register_detection_callback(self.simple_callback)
        self.loop = asyncio.get_event_loop()
        self.macs = []

    def handle_message(self):
        try:
            Domoticz.Debug("Entering message handler")
            while True:
                values = self.message_queue.get(block=True)
                if values is None:
                    Domoticz.Debug("Exiting message handler")
                    self.message_queue.task_done()
                    break

                # create sensor if needed
                if values.address not in self.macs and Parameters["Mode1"] == 'auto':
                        self.macs.append(values.address)
                        sensor_number = self.macs.index(values.address) + 2
                        Domoticz.Device(Name=values.address, Unit=sensor_number, TypeName="Temp+Hum", Used=1).Create()
                        self.save_macs_to_database(self.macs)

                # update values for known devices
                if values.address in self.macs:
                    sensor_number = self.macs.index(values.address) + 2

                    # humidity stat
                    hum = values.humidity
                    hum_stat = 0
                    if hum < 30:
                        hum_stat = 2
                    elif 30 <= hum < 45:
                        hum_stat = 0
                    elif 45 <= hum < 70:
                        hum_stat = 1
                    elif hum >= 70:
                        hum_stat = 3

                    # Signal level
                    signal_level = int(5 - (-50 - values.rssi)/10)
                    Domoticz.Debug("signal level: %.0f, %d" % (values.rssi, signal_level))

                    value = "%.1f;%d;%d" % (values.temperature, values.humidity, hum_stat)
                    Devices[sensor_number].Update(nValue=0, sValue=value, SignalLevel=signal_level, BatteryLevel=values.battery_level)

                self.message_queue.task_done()
        except Exception as err:
            Domoticz.Error("handleMessage: "+str(err))

    def simple_callback(self, device: BLEDevice, advertisement_data: AdvertisementData):
        try:
            if XIAOMI_LYWSD03MMC_PROFILE_CUSTOM in advertisement_data.service_data:
                service_data = advertisement_data.service_data[XIAOMI_LYWSD03MMC_PROFILE_CUSTOM]
                values = XiaomiLYWSD03MMC()
                values.address = ':'.join('{:02x}'.format(x) for x in service_data[0:6])
                values.temperature = float(int.from_bytes(service_data[6:8], byteorder='big')) / 10
                values.humidity = service_data[8]
                values.battery_level = service_data[9]
                values.battery_voltage = int.from_bytes(service_data[10:12], byteorder='big')
                values.frame = service_data[12]
                values.rssi = device.rssi

                # was the frame already received
                send = False
                track = self.keeping_track.get(values.address)
                if track:
                    if values.frame != track.frame:
                        send = True
                else:
                    send = True

                if send:
                    self.keeping_track[values.address] = values
                    Domoticz.Debug('device.address: %s' % device.address)
                    Domoticz.Debug('keeping_track: %d' % len(self.keeping_track))
                    self.message_queue.put(values)
        except Exception as err:
            Domoticz.Error("simple_callback: " + str(err))

    async def run(self):
        scanner = BleakScanner()
        scanner.register_detection_callback(self.simple_callback)

        # await scanner.discover()
        await scanner.start()
        await asyncio.sleep(5.0)
        await scanner.stop()

    def handle_ble(self):
        try:
            Domoticz.Debug("Scanner")

            while True:
                if self.ble_queue and not self.ble_queue.empty():
                    message = self.ble_queue.get(block=True)
                    if message is None:
                        Domoticz.Debug("Exiting ble handler")
                        self.ble_queue.task_done()
                        break
                if Devices[1].nValue == 1:
                    Domoticz.Debug("Scan")
                    self.loop.run_until_complete(self.run())
                else:
                    Domoticz.Debug("Scanner is disabled")
                    time.sleep(5.0)

        except Exception as err:
            Domoticz.Error("handle_ble: " + str(err))

    # function to create corresponding sensors in Domoticz if there are Mi Flower Mates which don't have them yet.
    def create_sensors(self):
        # create the domoticz sensors if necessary
        if len(Devices) - 1 < len(self.macs):
            Domoticz.Debug("Creating new sensors")
            # Create the sensors. Later we get the data.
            for idx, mac in enumerate(self.macs):
                Domoticz.Debug("Creating new sensor:" + str(mac))
                sensor_number = idx+2
                if sensor_number not in Devices:
                    Domoticz.Device(Name=str(mac), Unit=sensor_number, TypeName="Temp+Hum", Used=1).Create()
                    Domoticz.Log("Created device: " + Devices[sensor_number].Name)

    @staticmethod
    def parse_csv(csv):
        listvals = []
        for value in csv.split(","):
            listvals.append(value)
        return listvals

    @staticmethod
    def load_macs_from_database():
        # first, let's get the list of devices we already know about
        database = shelve.open('XiaomiLLYWSD03MMC')
        try:

            knownSensors = database['macs']
            oldLength = len(knownSensors)
            Domoticz.Debug("Already know something:" + str(oldLength))
            Domoticz.Log("Already known devices:" + str(knownSensors))
        except:
            knownSensors = []
            database['macs'] = knownSensors
            Domoticz.Debug("No existing sensors in system?")

        database.close()
        return knownSensors

    @staticmethod
    def save_macs_to_database(macs):
        # first, let's get the list of devices we already know about
        database = shelve.open('XiaomiLLYWSD03MMC')
        database['macs'] = macs
        database.close()
        return macs

    def onStart(self):
        Domoticz.Debug("Xiaomi LYWSD03MMC - devices made so far (max 255): " + str(len(Devices)))

        if Parameters["Mode6"] != "0":
            Domoticz.Debugging(int(Parameters["Mode6"]))
            DumpConfigToLog()

        # create master toggle switch
        if 1 not in Devices:
            Domoticz.Log("Creating the master Xiaomi LYWSD03MMC poll switch. Flip it to poll the sensors.")
            # default SwitchType, not enabled by default
            Domoticz.Device(Name="scanner", Unit=1, Type=244, Subtype=62, Image=9, Used=1).Create()

        # get the mac addresses of the sensors
        if Parameters["Mode1"] == 'auto':
            Domoticz.Log("Automatic mode is selected")
            self.macs = self.load_macs_from_database()
        else:
            Domoticz.Log("Manual mode is selected")
            self.macs = self.parse_csv(Parameters["Mode2"])
            self.create_sensors()

        self.message_thread.start()
        self.ble_thread.start()
        Domoticz.Heartbeat(5)

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        if Command == 'On':
            value = 1
        else:
            value = 0

        Domoticz.Debug("value: %d" % value)
        Devices[Unit].Update(nValue=value, sValue='')

    def onHeartbeat(self):
        Domoticz.Debug("Heartbeat test message")

    def onStop(self):
        # Not needed in an actual plugin
        for thread in threading.enumerate():
            if thread.name != threading.current_thread().name:
                Domoticz.Log("'"+thread.name+"' is running, it must be shutdown otherwise Domoticz will abort on plugin exit.")

        # signal queue thread to exit
        self.ble_queue.put(None)
        self.message_queue.put(None)
        Domoticz.Log("Clearing message queue...")
        self.message_queue.join()
        self.ble_queue.join()

        # Wait until queue thread has exited
        Domoticz.Log("Threads still active: "+str(threading.active_count())+", should be 1.")
        while (threading.active_count() > 1):
            for thread in threading.enumerate():
                if (thread.name != threading.current_thread().name):
                    Domoticz.Log("'"+thread.name+"' is still running, waiting otherwise Domoticz will abort on plugin exit.")
            time.sleep(1.0)


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

# Generic helper functions
def stringOrBlank(input):
    if (input == None): return ""
    else: return str(input)


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
