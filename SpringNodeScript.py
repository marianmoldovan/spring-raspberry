#!/usr/bin/Python2.7
# -*- coding: utf-8 -*-
import time
import pprint
import requests
import json
import sys
import pickle

#class made to recover from z-way-server the sensor data
#gets the ip addres
#returns the data
class ZWay:
    def __init__(self, address):
        #server ip & port:
        self.address = address

        #constants values of the ZWaveAPI
        self.getAllDataURL = 'ZWaveAPI/Data/0'
        self.getDeviceDataURL_1 = 'ZWaveAPI/Run/devices['
        self.getInquireURL = '].instances[0].commandClasses[0x31].Get()'
        self.getDeviceDataURL_2 = '].instances[0].commandClasses[0x31].data'


    def performGetRequest(self):

        #search for connected devices
        deviceN_=self.getDevices()
        data=Render()
        #TODO:test the devices that have no relevant data
        
        #for each one of the devices try to pull data
        for deviceNum in deviceN_ :        
            #obtains last updateTime from the sensor
            timeStam = data.getSensorUpdateTime(self.getRequest(self.getDeviceDataURL_1+str(deviceNum)+self.getDeviceDataURL_2,'OK'))
            
            #inquires the devices for new data
            self.getRequest(self.getDeviceDataURL_1+str(deviceNum)+self.getInquireURL,None)
            
            #obtains again the updateTime from sensor
            timeStam2 = data.getSensorUpdateTime(self.getRequest(self.getDeviceDataURL_1+str(deviceNum)+self.getDeviceDataURL_2,'OK'))
            #print 'inital time stamp: ',timeStam, ' actual time: ',time.time(), ' update time:',timeStam2
            #while the data has not been updated wait for 1 minute
            info = None
            while (timeStam >= timeStam2):
                #enquires again for UpdateTime
                print "waiting for sensor response..."

                time.sleep(10)
                info= self.getRequest(self.getDeviceDataURL_1+str(deviceNum)+self.getDeviceDataURL_2,'OK')
                timeStam2 = data.getSensorUpdateTime(info)

            #new instances of the render clas that will be entitled to feed the Spring api server with the proper data
            if (not info == None):
                data.initiate( info)
            else:
                 raise MyException(str(e)), None, sys.exc_info()[2]



    def getSensorUpdateTime(self,jsonData):
        resp=None
        try:
            for id_, item in jsonData['1'].iteritems():
                if id_ == 'updateTime':
                    resp = item
        except Exception as e:
            print 'ERROR during updating the Sensor Time:'
            raise MyException(str(e)), None, sys.exc_info()[2]
        return resp


    def getDevices(self):
        
        devicesList = []
        jsonDev=self.getRequest(self.getAllDataURL,'OK')
        try:
            for id_, item in jsonDev['devices'].iteritems():
                if id_ != '1':
                    devicesList.append(id_)
                

        except Exception as e:
            print 'ERROR during searching for devices'
            raise MyException(str(e)), None, sys.exc_info()[2]
            return None

        return devicesList


    def getRequest(self,direction,err):
        resp = None
        try:
            print 'Sending a get request to: ',self.address+direction
            response = requests.get(self.address+direction)
            result=response.status_code
            if (result == 200 and err != None):
                resp = response.json()
            elif (result == 200 and err == None):
                resp = 'OK'
        except Exception as e:
            print 'ERROR sending a get request to this direction:',direction
            raise MyException(str(e)), None, sys.exc_info()[2]
        return resp



#TODO:update this class to check for mail, uuid, apikey in config file
#class that verifies if is a real user
class Initial:
    def __init__(self):
        print 'Checking the user data'

    #start the verification
    def initiate(self):

        #if there is no conf file registrer new user
	if self.isNew() == True:
            self.userData()   
        else:
            print 'User allready registered'

    #try to get & store the user data
    def userData(self):
        try:
        #get user data		
            apiKey=raw_input("Please enter Api Key: ")
            usr=raw_input("Please enter your user: ")
            pwd=raw_input("Please enter your password: ")

            #try to authenticate the input data
	    if self.authenticate(usr,pwd,apiKey) == True:
                self.storeUser(usr,pwd,apiKey)
            else:
                print 'The input data is not valid'
               
               
        except IOError as e:
            print 'ERROR: _userData :',e.strerror

    #query the server
    def authenticate(self,user,pwd,apiKey):
        print 'Amos a meter la autenticacion aqui :)'
        return True
    
    #store the user data into a file
    def storeUser(self,user,pwd,apiKey):
        print '__storeUser' 
        try:
            fileM= FileManager()
            fileM.writeFile('user',user)        
            fileM.writeFile('pwd',pwd)  
            fileM.writeFile('apiKey',apiKey)
            print 'Succed to save user data'
        except IOError as e:
            print 'ERROR: _storeUser: ',e.strerror 

    #serch for the config file
    def isNew(self):
        isInit=None
        try:
            file=open('config.txt')
            isInit=False    
        except:
            isInit=True
        return isInit


#class that returns a json with the specified values
class TempJsonModel():
    def __init__(self,temp='',hum='',lux=''):
        self.temperature=temp
        self.humidity=hum
        self.light=lux
        self.addData()

    def addData(self):
        fileM=FileManager()
        self.uuid=fileM.readFileKeys("uuid")
        self.lat=0
        self.lon=0
 
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



#class that models the data obtained from the api
class SensorsModel():

    def __init__(self,typeA='',timeA='',valueA='',scaleA=''):
        self.typeS=typeA
        self.timeS=timeA
        self.valueS=valueA
        self.scaleS=scaleA

#render class
class Render:
    def __init__(self):
        self.MAXFIELDS=10
        self.MINFIELDS=1    
        self.sensorList=[]
        
        print 'Processing the data'
    
    def initiate(self, sensorData):
        print 'initiate sensorData'
        try:
            for i in range (self.MINFIELDS,self.MAXFIELDS):
                if str(i) in sensorData:
                    self.processFields(self.recoverFields(sensorData,str(i)))
            jsons=self.mountJSON()
            self.sendDataSpring(jsons)
        except BaseException as e:
            raise MyException(str(e)), None, sys.exc_info()[2]

    def sendDataSpring(self,jsonData):
        try:
            data=FileManager()

            head1 = "Content-Type"
            head2 = "Authorization"
            value1 = "application/json"
            value2 = "ApiKey "+data.readFileKeys("mail")+":"+data.readFileKeys("ApiKey")
            url="http://springsmartcity.com/api/1.0/weather/"
            header={head1:value1,head2:value2}
            print url,header
            print jsonData
            response = requests.post(url,data=jsonData,headers=header)
            result=response.status_code
            if (result == 201):
                print "data sucesfull send!"
            else:
                print "ERROR:",result
        except Exception as e:
            print 'ERROR sending the post request to this direction:'
            raise MyException(str(e)), None, sys.exc_info()[2]


    def getSensorUpdateTime(self,jsonData):
        resp=None
        try:
            for id_, item in jsonData['1'].iteritems():
                if id_ == 'updateTime':
                    resp = item
        except Exception as e:
            print 'ERROR during updating the Sensor Time:'
            raise MyException(str(e)), None, sys.exc_info()[2]
        return resp

    def mountJSON(self):
        try:
            dat=TempJsonModel()            

            for i in self.sensorList:
                #print i.typeS,i.valueS,i.timeS,i.scaleS
                if i.typeS == 'Humidity':
                    dat.humidity=i.valueS
                elif i.typeS == 'Luminiscence':
                    dat.light=i.valueS
                elif i.typeS == 'Temperature':
                    dat.temperature=i.valueS
            return dat.to_JSON()

        except Exception as e:
            raise MyException(str(e)), None, sys.exc_info()[2]
            return None

    def recoverFields(self,data,position):
        try:
            nuevo=SensorsModel()                   
            for id_, item in data[position].iteritems():
                if id_ == 'sensorTypeString':
                    nuevo.typeS = self.getValue(item)                  
                elif id_ == 'val':
                    nuevo.valueS = self.getValue(item)
                    nuevo.timeS = self.getTime(item)
                elif id_ == 'scaleString':
                    nuevo.scaleS=self.getValue(item)
            return nuevo
        except Exception as e:
            raise MyException(str(e)), None, sys.exc_info()[2]
            return None

    def getValue(self, diction):
        try:
            for id_, item in diction.iteritems():
                if id_ == 'value' :
                    return item
        except Exception as e:
            raise MyException(str(e)), None, sys.exc_info()[2]
            return None

    def getTime(self, diction):
        try:
            for id_, item in diction.iteritems():
                if id_ == 'updateTime' :
                    return item
        except Exception as e:
            raise MyException(str(e)), None, sys.exc_info()[2]
            return None

#        raise MyException('Not Implemented yet')

    def processFields(self,model):
        try:
            if not model == None:
                self.sensorList.append(model)
        except Exception as e:
            raise MyException(str(e)), None, sys.exc_info()[2]


#own type of exception
class MyException(Exception): pass        


#class that manages the config file
class FileManager():
    def __init__(self):
        nothing=''
        self.fName='/tmp/Spring/springConfig.txt'
        #manage the conf file
    
    def readFileLines(self):
        try:
            fileS=open(self.fName)
            lines = [line.strip() for line in fileS]
            fileS.close()
            return lines    
        except Exception as e:
            raise MyException(str(e)), None, sys.exc_info()[2]
            return none

    def readFileKeys(self,keyS):
        try:
            lines = self.readFileLines()
            for line in lines:
                key,value=line.split('=')
                if key == keyS:
                    return value
        except Exception as e:
            raise MyException(str(e)), None, sys.exc_info()[2]
            return none

    def writeFile(self,key,value):
        try:
            f=open(self.fName,'a')
            f.write(key+'='+value+'\n');
            f.close()    
        except Exception as e:
            raise MyException(str(e)), None, sys.exc_info()[2]


    
    

print '**********  Spring newtwork ***********\n'

#Test class instances

#inI=Initial()
#inI.initiate()

#reads the server ip from config file
z = ZWay(FileManager().readFileKeys("ip"))
#request to server
resp = z.performGetRequest()
print '\n **********  Spring newtwork ***********\n'
