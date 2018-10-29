#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# QUXA is a QUIC User eXperience Assesment experiment tool
#
# Copyright © 2018 CNES
#
# This file is part of the OpenBACH testbed.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY, without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see http://www.gnu.org/licenses/.


"""CPU Logger"""
__author__ = 'Ludovic Thomas'

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
