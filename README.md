# Domoticz Xiaomi LYWSD03MMC - plugin
Plugin for Domoticz to auto create Temperature and Humidity sensors


## preperation
```
copy plugin folder to domoticz/plugins - folder

install python plugins
pip install -r requirements.txt

restart domoticz
```
### hardware
create new hardware with type Xiaomi LYWSD03MMC

### Xiaomi LYWSD03MMC switch
after installation of the hardware, the plugin will create a "master" switch to enabled Bluetooth scanning.
Default state if OFF, switch to ON to start scanning

### automatic creation or manual creation of sensors.
this plugin keeps track of the created sensors by writing to a shelve database.
check if domoticz had control to create and modify this database in the domoticz directory
