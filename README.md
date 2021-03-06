# Domoticz Xiaomi LYWSD03MMC - plugin
Plugin for Domoticz to auto create Temperature and Humidity sensors


## installation

Check you do actually have a version of Python3, it will tell you if it is installed already:
```
sudo apt-get update
sudo apt install python3
```
Check the version:
```
python3 -V
```
Make sure that you have libpython installed, it needs to match the version you have. If you have Python 3.4.x then you make sure you have libpython3.4, if you have Python 3.5.x then you make sure you have libpython3.5 and so on. Use this command to check:
```
dpkg --get-selections | grep libpython
```
If it is not there then use (where 'x' is the version from above: e,g libpython3.4 or libpython3.5 etc):
```
sudo apt install libpython3.x
```
Some users believe that Domoticz Beta versions since V3.6129 require Python3-dev. Unconfirmed, only install if you are having issues:
```
sudo apt install python3-dev
```
Install pip
```
sudo apt-get install python3-pip
```

Restart Domoticz.
```
sudo systemctl restart domoticz.service
```

### Git clone
Install Git to easily download the plugins through the terminal:
```
sudo apt-get update
sudo apt-get install git
```

Clone plugin to domoticz/plugins - folder
```
cd domoticz/plugins
git clone https://github.com/arnojdejong/DomoticzXiaomiLYWSD03MMC.git
```

### Install python plugins
```
cd DomoticzXiaomiLYWSD03MMC
sudo pip3 install -r requirements.txt

sudo systemctl restart domoticz.service
```

### extra info
Install domoticz
```
curl -L https://install.domoticz.com | sudo bash
```
org.freedesktop.DBus.Error.TimedOut: Failed to activate service 'org.bluez': timed out<br/>
Reboot needed
```
sudo reboot
```

Domoticz link, python3<br/>
https://www.domoticz.com/wiki/Using_Python_plugins

## Domoticz
### new hardware
Create new hardware in domoticz with type: Xiaomi LYWSD03MMC<br/>
<br/>
This plugin creates devices, make sure "Accept new Hardware Devices" is on. (Setup -> Settings -> Hardware/Devices -> Accept new Hardware Devices)
### Xiaomi LYWSD03MMC switch
After installation of the hardware, the plugin will create a "master" switch to enabled Bluetooth scanning.<br/>
Default state if OFF, switch to ON to start catching the bluetooth advertisements

### automatic creation or manual creation of sensors.
This plugin keeps track of the created sensors by writing to a shelve database.<br/>
Check if Domoticz has the rights to create and modify this database in the domoticz directory<br/>
If manual mode is selected enter the macs of the sensors in the field (Mode2), eg: "aa:bb:cc:dd:ee:ff", "aa:bb:cc:dd:ee:00"

### Debug
This plugin has a debug option if needed<br/>
(Setup -> Hardware -> <hardware> -> Debug (off / all) -> Update)
