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


"""Tests units scheduler program"""
__author__ = 'Ludovic Thomas'

#This is the scheduler, a script that launches the test units.

###################### CONFIG #############################
# Please complete the following parameters
# WARNING : Time values have to be provided in UTC
#### Test start time
start_time_year = 2018
start_time_month = 9
start_time_day = 3
start_time_hour = 11
start_time_minute = 0
#### Test stop time
stop_time_year = 2018
stop_time_month = 9
stop_time_day = 3
stop_time_hour = 15
stop_time_minute = 20
#### Test interval
interval_day = 0
interval_hour = 0
interval_minute = 5
#### Extra delay after the use of optionnal options
extra_delay_minute = 5
# When "extra options" are used, this extra delay will be added after the completion of the test unit.
# This is to compensate the fact that test units with extra options need more time to complete.
#### Command to launch
command = ["mate-terminal","-e" ,"sudo python3 main_process.py --mail"]
optionnal_command = " --qos --weather"
#Use optionnal command every n_tests_optionnal test units.
n_test_optionnal = 5

#################### END CONFIG ###########################


from datetime import datetime, timedelta
import time
import os
import subprocess
import copy

#Counter of test units performed since last "extra option"
counter_qos = 0
#Check root
if os.geteuid() != 0:
    exit("Sorry, you need to be root to launch this script !")

#Get time
a = datetime.utcnow()
start_time = a.replace(year=start_time_year, month=start_time_month, day=start_time_day, hour=start_time_hour, minute=start_time_minute)
stop_time = a.replace(year=stop_time_year, month=stop_time_month, day=stop_time_day, hour=stop_time_hour, minute=stop_time_minute)
if(start_time < a):
    seconds_to_wait_before_start = 0
else:
    seconds_to_wait_before_start = (start_time - a).total_seconds()

print("[Scheduler] Waiting " + str(seconds_to_wait_before_start) + " seconds before start")
time.sleep(seconds_to_wait_before_start)
a = datetime.utcnow()
#As long as we dont reach the stop time
while(a < stop_time):
    to_add_extra = timedelta(days=0, hours=0, minutes=0)
    #Creating the command, including extra options if necessary and computing extra delay
    if(counter_qos == 0):
        myCommand = copy.deepcopy(command)
        myCommand[2] = myCommand[2] + optionnal_command
        to_add_extra = timedelta(days=0, hours=0, minutes=extra_delay_minute)
    else:
        myCommand = copy.deepcopy(command)
    #Increasing the counter
    counter_qos = counter_qos + 1
    if(counter_qos >= n_test_optionnal):
        counter_qos = 0
    #Execute command
    p = subprocess.Popen(myCommand, env=os.environ.copy())
    #Wait for next interval
    a = datetime.utcnow()
    to_add = timedelta(days=interval_day, hours=interval_hour, minutes=interval_minute)
    next_wake_up = a + to_add + to_add_extra
    if(next_wake_up > a):
        seconds_to_wait_before_interval = (next_wake_up-a).total_seconds()
        print("[Scheduler] Waiting " + str(seconds_to_wait_before_interval) + " seconds before next interval")
        time.sleep(seconds_to_wait_before_interval)
    a = datetime.utcnow()
print("[Scheduler] Stop time reached")
