############################ CONFIG ############################
# Please complete the following parameters
user_name = "username"
#Put here the linux username of the user that will launch the test. This is mandatory to deal with sudo/non-sudo scripts
browsers_list = ["ChromeNoQuic", "ChromeQuic"]
#List of browsers to test
browers_scripts_dictionnary = {
    "ChromeNoQuic" : "chrome_script.py",
    "ChromeQuic" : "chrome_script.py --quic"
}
#Dictionnary that give the name of the test script for the related browser
browsers_targetProcess_dictionnary = {
    "ChromeNoQuic" : "chrome",
    "ChromeQuic" : "chrome"
}
#Targets to find for Strace (name of the program)
ip_target = "my.page.ip.address"
#Please write here the ip adress of the server holding the webpage.
cpuUsage_scriptFile = "cpu_logger.py"
#Name of the cpu script
interface = "my_interface"
#Interface to listen to
tcpdump_interface = " -i " + interface + " "
#tcpdump_filter = "tcp and port 80 or port 443"
tcpdump_filter = ""
#Tcp dump filter to use when logging traffic
folderOutput = "/tmp/"
#Output location for the files
tcpdump_logFilePrefix = "trafficCapture_"
tcpdump_logFilePostfix = ".log"
#Prefix/Postfix of the pcap file 
cpuUsage_logFilePrefix = "cpuUsage_"
cpuUsage_logFilePostfix = ".log"
#Prefix/Postfix of the cpu usage file
loadTimeResults_logFilePrefix = "loadTime_"
loadTimeResults_logFilePostfix = ".log"
#Prefix/Postfix of the browser performance file
qos_logFilePrefix = "qosMetrics_"
qos_logFilePostFix = ".log"
#Prefix/Postfix of the QoS log file
weather_delay_minutes = 30
#Time to wait after the test is finished before requesting weather data
mail_api_key = "my-api-key"
mail_api_secret = "my-api-secret"
#Configuration to send email notifications of the test Please see mailjet.com
my_from_address = "ano.nymous@anonymous.com"
my_from_name = "Ano Nymous"
#Sender of the notification email. Check mailjet's website for more info
my_recipient = "James.Holden@rossinante.space"
#Recipient of the notification email

######################### END CONFIG ####################################

import subprocess
import os
import sys
import time
from datetime import datetime, timedelta
import argparse
import string
import psutil
import iperf_run
import weather_api
import mailjet_rest
import my_strace
import random


def prepare_iptables(prepare=True):
    "Prepare rules for iptables"
    print("[main] Peparing iptables ...")
    command = "iptables -F"
    print("\t" + command)
    subprocess.call(command.split())
    command = "iptables -X"
    print("\t" + command)
    subprocess.call(command.split())
    if(prepare):
        command = "iptables -A OUTPUT -d %s -p udp --dport 443 -j ACCEPT" % ip_target
        print("\t" + command)
        subprocess.call(command.split())
        command = "iptables -A OUTPUT -p udp --dport 443 -j DROP"
        #Drop udp (except to target)
        print("\t" + command)
        subprocess.call(command.split())
    print("Done")

#Parse args
parser = argparse.ArgumentParser(description='Tool for automated benchmark')
parser.add_argument('--qos', action='store_true', help='Perform QoS report')
parser.add_argument('--ilog', action='store_true', help='Enable internal log of the browser')
parser.add_argument('--weather', action='store_true', help='Register the weather')
parser.add_argument('--mail', action='store_true', help='Send an email when test is finished')
parser.add_argument('--strace', action='store_true', help='Record system calls using strace')
args = parser.parse_args()
#Check sudo rights
if os.geteuid() != 0:
    sys.exit("Sorry, you need to be root to launch this script !")
#Getting origin time stamp
origin_time = time.time()
origin_time_string = datetime.utcfromtimestamp(origin_time).strftime("%Y-%m-%d-%H%M-%SZ")
#Taking reference for data consumption
sent_before = psutil.net_io_counters(pernic=True)[interface][0]
received_before = psutil.net_io_counters(pernic=True)[interface][1]
print("--------------- [main] ----------------")
print("Starting test unit : " + origin_time_string)
print("---------------------------------------")
#Build non-sudo command prefix
nonSudoCommandPrefix = "su " + user_name + " --preserve-environment -c"
#Register link QoS
myIperf = iperf_run.Iperf3Command(folderOutput, origin_time_string)
if(args.qos):
    myIperf.do_iperf()
    myIperf.do_ping_primary()
else:
    myIperf.do_ping_primary(True)
if(args.ilog):
    ilog_option = "1"
else:
    ilog_option = "0"

#Randomize the order in which to test the browsers
random.shuffle(browsers_list)
#Configure iptables
prepare_iptables()
#For each browser to test
for browser in browsers_list:
    #Build filenames
    filename_trafficCapture = tcpdump_logFilePrefix + browser + "_" + origin_time_string + tcpdump_logFilePostfix
    filename_cpuUsage = cpuUsage_logFilePrefix + browser + "_" + origin_time_string + cpuUsage_logFilePostfix
    #Build commands
    command_trafficCapture = "tcpdump -w " + folderOutput + filename_trafficCapture + tcpdump_interface + tcpdump_filter
    command_cpuUsage = "python3 " + cpuUsage_scriptFile + " " + folderOutput + filename_cpuUsage
    command_loadTimeResults = "python3 " + browers_scripts_dictionnary[browser] + " --out=" + folderOutput + " --time=" + origin_time_string + (" --ilog" if args.ilog else "")
    #Build command list
    command_trafficCapture_list = command_trafficCapture.split()
    command_cpuUsage_list = nonSudoCommandPrefix.split() + [command_cpuUsage]
    command_loadTimeResults_list = nonSudoCommandPrefix.split() + [command_loadTimeResults]
    #Strace
    if(args.strace):
        straceModule = my_strace.Strace(browsers_targetProcess_dictionnary[browser], folderOutput, browser, origin_time_string)
    #Launching processes
    trafficCapture_proc = subprocess.Popen(command_trafficCapture_list)
    cpuUsage_proc = subprocess.Popen(command_cpuUsage_list)
    myEnv = os.environ.copy()
    time.sleep(5) #Delay 3 sec to let recorders record
    if(args.strace):
        straceModule.start()
    loadTimeResults_proc = subprocess.Popen(command_loadTimeResults_list, env=myEnv)
    #Wait for test script to end
    loadTimeResults_proc.wait()
    time.sleep(5) #Delay 10 sec to let cpu usage drop again
    #Terminating other processes
    if(args.strace):
        straceModule.stop()
    trafficCapture_proc.terminate()
    cpuUsage_proc.terminate()
    time.sleep(2)

#Reset iptables config
prepare_iptables(False)
#Computing consumption and duration
sent_after = psutil.net_io_counters(pernic=True)[interface][0]
received_after = psutil.net_io_counters(pernic=True)[interface][1]
total_duration = (time.time() - origin_time)
print("--------------- [main] ----------------")
print("Test unit " + origin_time_string + " terminated.")
print("Total duration : %.0fs" % total_duration)
print("Total sent : %.2f MB" % ((sent_after - sent_before) / 1000000))
print("Total received : %.2f MB" % ((received_after - received_before) / 1000000))
print("---------------------------------------")
if(args.weather):
    #If weather is requested
    weather_now = datetime.utcnow()
    to_wait = timedelta(seconds=60 * weather_delay_minutes)
    weather_expected = weather_now + to_wait
    print("Now waiting " + weather_expected.strftime("%Y-%m-%d-%H%M-%SZ") + " to ask weather...")
    #Wait for 30 minutes (delay of the weather reports)
    time.sleep(60 * weather_delay_minutes)
    #Request weather
    myWeather = weather_api.WeatherChecker(folderOutput, origin_time_string)
    myWeather.requestWeather()
#If requested, send an email to inform end of test
if(args.mail):
    myMail = mailjet_rest.Client(auth=(mail_api_key, mail_api_secret))
    data = {
        'FromEmail' : my_from_address,
        'Fromame' : my_from_name,
        'Subject' : 'Test Notification',
        'Text-part' : 
            "Test notification\n Test unit : " + origin_time_string + ("\n Total duration : %.0fs" % total_duration) + ("\n Total sent : %.2f MB" % ((sent_after - sent_before) / 1000000)) + ("\n Total received : %.2f MB" % ((received_after - received_before) / 1000000)) + ("\n qos=%r\n weather=%r\n ilog=%r\n email=%r\n" % (args.qos, args.weather, args.ilog, args.mail)),
        'Recipients' : [
                {
                    "Email" : my_recipient
                }
            ] 
        }
    result = myMail.send.create(data=data)
time.sleep(10)
