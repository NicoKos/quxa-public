################### Config #####################
# Please configure the following parameters
target = "https://www.google.com/test.html"      
#Enter here as a string the full path of the webpage to be retrieved.
nb_load = 3
#Enter here the number of sucessive loads to perform before ending the test
release_time_min = 5
#Enter here the lower bound for the random cool down duration between two sucessive loads in seconds.
release_time_max = 15
#Enter here the upper bound for the random cool down duration between two sucessive loads in seconds
################# End Config ###################

import os
import sys
import shlex
from datetime import datetime
from selenium import webdriver
from selenium import common
from selenium.webdriver.chrome.options import Options
import time
import copy
import argparse
import random

enable_quic_command = "chrome.send('enableExperimentalFeature',['enable-quic' + '@' + 1, 'true'])"
disable_quic_command = "chrome.send('enableExperimentalFeature',['enable-quic' + '@' + 2, 'true'])"
enable_fastopen_command  = "chrome.send('enableExperimentalFeature', ['enable-tcp-fast-open', 'true'])"
#Commands to use to enable/disable some experimental flags

target2 = "chrome://flags"

def chrome_configure_experimental_flags(myDriver, quic):
    "Function that configure the experimental flags of Chrome"
    myDriver.get('chrome://flags')                      #Load page where configuration javascript commands are allowed
    if(quic):
        myDriver.execute_script(enable_quic_command)    #Enable QUIC
    else:
        myDriver.execute_script(disable_quic_command)   #Disable QUIC
    myDriver.execute_script(enable_fastopen_command)    #Enable TCP FO
    myDriver.get('chrome://flags')                      #Re-load so that we can check
    time.sleep(5)                                       #Give some time to visually check the flags
      
parser = argparse.ArgumentParser(description='Chrome script')
parser.add_argument('--out', action='store', help='Destination folder for the results')
parser.add_argument('--time', action='store', help='Time reference as a string')
parser.add_argument('--ilog', action='store_true', help='Internal logging')
parser.add_argument('--quic', action='store_true', help='Use QUIC')
args = parser.parse_args()
#Parsing the args
if os.geteuid() == 0:
    sys.exit("Sorry, this script can't be run as sudo!")
#Checking sudo rights


folder_output = args.out
time_string = args.time
ilog_option = args.ilog
chromeQuicSuffix = ""
if(not args.quic):
    chromeQuicSuffix = "NoQuic"
else:
    chromeQuicSuffix = "Quic"
#Preparing variables
logFileName = folder_output + "loadTime_Chrome" + chromeQuicSuffix + "_" + time_string + ".log"
logFile = open(logFileName, 'w')
#Opening logfile

#################### Starting test  ###################

print("[Chrome][%s] Starting test script ..." % chromeQuicSuffix)

### Building and configuring ###
myOptions = Options()
myOptions.add_argument("--disk-cache-size=1")
myOptions.add_argument("--media-cache-size=1")
#Disable content caching by providing too small buffer sizes
myOptions.add_argument("--quic-connection-options=TBBR")
#Set connection options to request BBR CC on server side when using QUIC
profile_folder = folder_output + 'profile_chrome' + chromeQuicSuffix +'_' + time_string
myOptions.add_argument("user-data-dir=" + profile_folder)
#Set our own, to be re-used, profile
driver = webdriver.Chrome(chrome_options=myOptions)
#Create driver
print("[Chrome][%s] Enabling experimental features ..." % chromeQuicSuffix, end='', flush=True)
chrome_configure_experimental_flags(driver, args.quic)
print("Done")
#Set experimental features
driver.close()
#Close driver (profile will be re-used)

### End building and configuring ###
try:
    for i in range(nb_load):
        myOptions_loop = copy.deepcopy(myOptions)
        #Copying the options structure cause we need to set the internal log system without messing everything up
        if(ilog_option):
            myOptions_loop.add_argument("--log-net-log=" + folder_output + 'chrome' + chromeQuicSuffix +  'NetworkCapture_' + time_string + "_" + str(i) + '.json')
            myOptions_loop.add_argument("--net-log-capture-mode=IncludeCookiesAndCredentials")
        #Setting the internal log system, if required
        start_time_gen = time.time()
        #Collecting start time
        driver = webdriver.Chrome(chrome_options=myOptions_loop)
        #Opening chrome. Here, we use a copy of the options but it includes the path to the same profile folder, so we'll keep the experimental flags.
        driver.get(target)
        #Retrieve the target. This call release after the loadEventEnd event.
        endTime = driver.execute_script("return window.performance.timing.loadEventEnd")
        startTime = driver.execute_script("return window.performance.timing.connectStart")
        responseStartTime = driver.execute_script("return window.performance.timing.responseStart")
        #Execute commands to retrieve the timings
        timeBeforeResponse = responseStartTime - startTime
        timeToLoad = endTime - startTime
        #Computing the PLT and TTR
        driver.get(target2)
        #Force unloading the page
        driver.close()
        #Close the driver
        time_gen = time.time() - start_time_gen
        #Compute global time required
        logFile.write(str(time.time()) + ";" + str(timeToLoad) + ";" + str(timeBeforeResponse) +  ";" + str(time_gen) + "\n")
        #Saving the resutls in the log file
        if((i+1) < nb_load):
            #If not the last load, wait a uniform random duration
            time.sleep(random.randint(int(release_time_min*1000),int(release_time_max*1000))/1000)
            del driver
            del myOptions_loop
        #Force loosing all states by deleting structures.
        
finally:
    print("[Chrome][%s] Test script finished" % chromeQuicSuffix )
    logFile.close()
    #Closing log file


