spring-raspberry
================

Spring Interface for raspberryPi sensors (based on Zwave API)====


Description
An custom user will be able to download from springsmartcity.com a tar file where there will be a config file, a pythonscript an readme file and the installation script (shell).



Files
For the prototype the config file must have the user data fields specified, such as:mail, uuid, ApiKey.
The install script will copy all the other files to a new directory and will add a new task in crontab that will run the python script each hour.
The python script uses the Zwave api server to detect devices connected to a raspberryPi and check if they are usefull to spring Grid (temp, light, humidity etc.). If so builds a post request using the config file data and the values recoverd from the server and sends them to Spring Api (weather).
