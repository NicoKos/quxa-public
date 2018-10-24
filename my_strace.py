#Process used to log the system calls

import subprocess
import psutil
import threading
import os

search_command = "ps ax | grep "

class Strace(object):
    def __init__(self, targetToFind, outfolder, browser, dateString):
        self.dateString = dateString
        self.target_pid = 0
        self.mainThread = None
        self.straceProcess = None
        self.counter = 0
        self.target_name = targetToFind
        self.outputFolder = outfolder
        self.browserName = browser
        self.doContinue = False
        print("[Strace] Module initiated : \n \t Process target name : %s \n \t Output folder : %s \n \t Browser name : %s" % (self.target_name, self.outputFolder, self.browserName))

    def start(self):
        self.doContinue = True
        self.mainThread = threading.Thread(target=self.mainLoop)
        self.mainThread.start()
        print("[Strace] Started")
    def mainLoop(self):
        while(self.doContinue):
            #Search for a PID that match the target :
            found = False
            while(not found and self.doContinue):
                for proc in psutil.process_iter():
                    if(proc.name() == self.target_name):
                        self.target_pid = proc.pid
                        found = True
                        break
            if(self.doContinue):
                filename = self.outputFolder + "strace_" + self.browserName + "_" + self.dateString + "_" + str(self.counter) + ".log"
                strace_command = "strace -o " + filename + " -p " + str(self.target_pid)
                self.straceProcess = subprocess.Popen(strace_command.split(), stdout=subprocess.STDOUT)
                self.straceProcess.wait()
                self.counter = self.counter + 1
    def stop(self):
        self.doContinue = False
        self.mainThread.join()
        print("[Strace] Stopped. Total captured cycles : %d" % self.counter)