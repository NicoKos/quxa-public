############### CONFIG ######################
target_qos = "ping.online.net" + " "
#Enter here the domain name (only,  not the full path) of the public iperf3 server to use for link quality measurement. Follow by a space.
target_primary = "google.com" + " "
#Enter here the domain name (only,  not the full path) of the server holding the target page. Follow by a space.
ports = range(5200,5210)                
#Range of port to test for iperf3. The script will cycle among them until it find a valid port or it reaches the attempt limitation
protocols = {" ", "-u -b 0 "}            
#Command suffix to test. First is TCP, second is UDP with no bandwith limitation
directions = {" ", "-R "}                
#Command suffix to test. First is Client->Server direction, second is Server->Client test
error_limit = 50                        
#Max of attempts generating errors before giving up. Usually, an error is triggered if the port was already used by another user
timeout_limit = 2                       
#Max of attempts generating timeouts before giving up. Usually, a timeout is triggered if the remote server is not up OR if a middlebox blocks the test
timeout_seconds = 30                   
#The timeout value in seconds. Recommended value is at least twice the time set after the '-t' option in 'command_first'
command_first = "iperf3 -J -t 15 -c "   
#The first part of the command, with the common options : -J to format output as JSON, -t 15 for 15seconds test, -c to set the mode as client.

############### END CONFIG ##########################

import subprocess
import threading
import json

## Definition of a class to handle the command
class Iperf3Command(object) :
    def __init__(self, outFolder, dateString):
        "Initialize the class"
        self.process1 = None
        self.process2 = None
        self.outFolder = outFolder
        self.dateString = dateString

    #Do only the ping to the primary target
    def do_ping_primary(self, doWrite=False):
        "Perform ping to the primary target"
        ping_command_primary = "ping -c 5 " + target_primary
        print("[Ping] Pinging target : <" + ping_command_primary + ">...", end="", flush=True)
        self.process1 = subprocess.Popen(ping_command_primary.split(), stdout=subprocess.PIPE)
        self.process1.wait()
        print("Done")
        # Export primary results
        if(doWrite):
            ping_outFilename = self.outFolder + "ping_primary_" + self.dateString + ".log"
            myFile = open(ping_outFilename,'wb')
            myFile.write(self.process1.stdout.read())
            myFile.close()

    #Perform the iperf
    def do_iperf(self) :
        "This function perfoms the link QoS test"
        #Start with ping tests
        ping_command_qos = "ping -c 20 " + target_qos
        ping_command_primary = "ping -c 20 " + target_primary
        print("[Ping] Pinging targets : \n\t<" + ping_command_qos + "> \n\t<" + ping_command_primary + ">...", end="", flush=True)
        self.process1 = subprocess.Popen(ping_command_qos.split(), stdout=subprocess.PIPE)
        self.process2 = subprocess.Popen(ping_command_primary.split(), stdout=subprocess.PIPE)
        self.process1.wait()
        self.process2.wait()
        print("Done")
        # Export qos results
        ping_outFilename = self.outFolder + "ping_qos_" + self.dateString + ".log"
        myFile = open(ping_outFilename,'wb')
        myFile.write(self.process1.stdout.read())
        myFile.close()
        # Export primary results
        ping_outFilename = self.outFolder + "ping_primary_" + self.dateString + ".log"
        myFile = open(ping_outFilename,'wb')
        myFile.write(self.process2.stdout.read())
        myFile.close()
        # Performing now iperf
        index = 0 #Index used for logfiles
        #For each tuple (protocol, direction) to test ...
        for protocol in protocols:
            for direction in directions:
                exit_test = False
                error_count = 0
                timeout_count = 0
                #While exit conditions not matched
                while(not exit_test):
                    #Test among each available server ports
                    for port in ports:
                        #Build command
                        command = command_first + target_qos + "-p " + str(port) + " " + direction + protocol

                        #Define a function to be called as a separate thread. This is used for handling the timeout
                        def targetTh():
                            print("[Iperf3][Attempt " + str(error_count + timeout_count) + "] <" + command + "> ... ", end="", flush=True)
                            #Launch the subprocess and wait
                            self.process1 = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                            self.process1.wait()

                        #Launche the thread and wait
                        thread = threading.Thread(target=targetTh)
                        thread.start()
                        thread.join(timeout=timeout_seconds)
                        success = True
                        #If thread still alive, this is a timeout
                        if(thread.is_alive()):
                            timeout_count = timeout_count +1
                            success = False
                            print("Timeout")
                            self.process1.terminate()
                            thread.join()
                        #Else, if retcode not 0, this is an error
                        elif(self.process1.returncode):
                            error_count = error_count +1
                            success = False
                            print("Error")
                        if(success):
                            fileName = self.outFolder + "qos_" + self.dateString + "_" + str(index) + ".log"
                            print("Success")
                            exit_test = True
                            myFile = open(fileName,'wb')
                            myFile.write(self.process1.stdout.read())
                            myFile.close()
                            index = index + 1
                            break
                        #Test for the exit conditions if they may break the for loop
                        if(not(error_count < error_limit) or not(timeout_count < timeout_limit)):
                            fileName = self.outFolder + "qos_" + self.dateString + "_" + str(index) + "_failed.log"
                            print("[Iperf3] Too much errors. Writing down results of last test")
                            exit_test = True
                            myFile = open(fileName,'wb')
                            myFile.write(self.process1.stdout.read())
                            myFile.close()
                            index = index + 1
                            break




if __name__ == '__main__' :
    myCommand = Iperf3Command("test", "log")
    myCommand.do_iperf()
