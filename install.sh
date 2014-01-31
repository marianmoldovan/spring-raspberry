#!/bin/bash

clear
echo "Installation is starting"

readmeF="README"
configF="springConfig.txt"
scriptF="SpringNodeScript.py"
springDir="/usr/local/Spring"


#check that readme, config & pythonscript are there
echo "Chek the existence of the needed files"

if [ -f $readmeF ]
then
	echo "Ok"
else
	echo "Error file README not found"
	exit 
fi

if [ -f  $configF ]
then
	echo "Ok"
else
	echo "$configF not found. Will create the file and add entry now."
	touch $configF
fi


if [ -f $scriptF ]
then
	echo "Ok"
else
	echo "Error script file not found"
	exit 
fi


#obtains & stores the local IP and adds the port (8083)
localIP=`ifconfig | grep  "inet addr:" | grep -v '127*'| awk '{print $2}'|cut -d ":" -f2 `


#stores the local ip
if [[ -n $localIP ]]; then
	echo "your server ip is: http://$localIP:8083/"
	echo "ip=http://$localIP:8083/" >> $configF
 
else
	echo "no Ip found. ${nl} Exiting.."
	exit
fi

#info message
echo "Now you need to enter all the data you got after loggin to Spring"

#stores the email in the config file
echo -n "Please enter your e-mail>"
read email
if [[ -n $email ]]; then
	echo "you entered:$email"
	echo "mail=$email" >> $configF
else
	echo "empty email, Exiting.."
	exit
fi

#stores the uuid in the config file
echo -n "Please enter your uuid>"
read uuid
if [[ -n $uuid ]]; then
	echo "you entered:$uuid"
	echo "uuid=$uuid" >> $configF

else
	echo "empty uuid, Exiting.."
	exit
fi

#stores the apiKey in the config file
echo -n "Please enter your ApiKey>"
read ApiKey
if [[ -n $ApiKey ]]; then
	echo "you entered:$ApiKey"
	echo "ApiKey=$ApiKey" >> $configF

else
	echo "empty ApiKey, Exiting.."
	exit
fi


#crear carpeta Spring y copiar alli esos ficheros
if [ ! -d $springDir ]
then
	sudo mkdir $springDir
fi
sudo cp -P $readmeF $configF $scriptF $springDir
cd $springDir
pwd
ls -l

#TODO:verificar version python e instalar pikle
#TODO:verificar que el servidor de zwave está levantado


#if crontab not exists create job
job="@hourly python $springDir/SpringNodeScript.py >> /var/log/spring_output.log 2>&1"

(sudo crontab -l ; echo -e "$job ${nl}" )| uniq -u| sudo crontab -

#TODO: autodistruction of the file
