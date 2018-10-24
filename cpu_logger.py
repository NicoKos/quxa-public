
import psutil
import sys
import signal
import time


def sigterm_handler(_signo, _stack_frame):
    print("[CpuLogger] Log terminated")
    logFile.close()
    exit(0)
#Defining a handler to manage the SIGTERM signal
print("[CpuLogger] Starting...")
signal.signal(signal.SIGTERM, sigterm_handler)
#Linkg the handler
logFileName = sys.argv[1]
logFile = open(logFileName, 'w')
#Opening the logfile
while 1:
    logFile.write(str(time.time()) + ";" + str(psutil.cpu_percent(interval=1))+ "\n")
#Logging until terminated.