# Domoticz Xiaomi LYWSD03MMC - plugin
Plugin for Domoticz to auto create Temperature and Humidity sensors


## preperation

### Python: Failed dynamic library load, install the latest libpython3.x library that is available for your platform.
```
sudo apt-get install python3.7 libpython3.7 python3.7-dev python3-pip -y

sudo systemctl restart domoticz.service
```

```
copy plugin folder to domoticz/plugins - folder

install python plugins
pip install -r requirements.txt

restart domoticz
```
### hardware
create new hardware with type Xiaomi LYWSD03MMC

### Xiaomi LYWSD03MMC switch
after installation of the hardware, the plugin will create a "master" switch to enabled Bluetooth scanning.<br/>
Default state if OFF, switch to ON to start scanning

### automatic creation or manual creation of sensors.
this plugin keeps track of the created sensors by writing to a shelve database.<br/>
check if domoticz had control to create and modify this database in the domoticz directory<br/>
if manual mode is selected enter the macs of the sensors in the field (Mode2), eg: "aa:bb:cc:dd:ee:ff", "aa:bb:cc:dd:ee:00"
