# Welcome
Welcome to the QUXA public repository.
QUXA is a QUIC User eXperience Assesment experiment.
We use Google Chrome with GQUIC to measure page load time.

# Deploy
We highly recommend that you perform all the test on a **dedicated** machine or virtual machine. 

First step is to install the necessary software :
To do so, we provide the install.sh script :

```bash
$ sudo ./install.sh
```

# Configure
 * First, find your own webpage on a GQUIC capable server somewhere in the internet.
 * Second, retrieve :
	- The full webpage path
	- The subdomain name
	- The ip adress of the server
 * Configure your /etc/hosts file so that DNS resolution is imposed for the subdomain to the ip adress.
 * Then, open **EACH** python script and complete the requested parameters between the *CONFIG* markers.

# Launch one test unit
Once configured, to launch one test unit :

```bash
$ sudo python3 main_process.py
```

# Launch several test units using the scheduler
You can use the scheduler (configure scheduler.py) to launch several test units.

```bash
$ sudo python3 scheduler.py
```

# Outputs
Depending on the options provided to main_process.py (see python3 main_process.py --help), the following outputs are created :

 * loadTime_\<browser_name\>_<test_unit_string>.log contains the page load time results as follow. 
	- For each load : <linux_time_at_which_the_line_was_written>;<Page_Load_Time_in_ms>;<Time_to_responseStart_in_ms>;<total_duration_open_to_close_in_s>
	- <browser_name> equals "ChromeQuic" or "ChromeNoQuic" (or anything indicated on the main_process.py header).
	- <test_unit_string> is the UTC time of the test as follow : YYYY-MM-DD-HHMM-SSZ
 * <browserName>NetworkCapture_<test_unit_string>_<load_index>.json is the json export of chrome internal logs. It can be openned using chrome://net-internals, page "import".
	- Json chrome specific format
	- <browserName> equals "chromeNoQuic" or "chromeQuic"
	- <test_unit_string> is the UTC time of the test as follow : YYYY-MM-DD-HHMM-SSZ
	- <load_index> is the load index (might for instance equal 0,1 or 2).
	- **Requires** --ilog option
 * cpuUsage_<browserName>_<test_unit_string>.log contains the cpu usage.
	- Every 2 seconds : <linux_time_at_which_the_line_was_written>;<cpu_usage_in_percent>
	- <browser_name> equals "ChromeQuic" or "ChromeNoQuic" (or anything indicated on the main_process.py header).
	- <test_unit_string> is the UTC time of the test as follow : YYYY-MM-DD-HHMM-SSZ
 * ping_<target_name>_<test_unit_string>.log contains the results of the ping program :
	- Ping output (special format)
	- <target_name> : primary : the server holding the page. qos : the server used for link quality measurements.
	- <test_unit_string> is the UTC time of the test as follow : YYYY-MM-DD-HHMM-SSZ
 * qos_<test_unit_string>_<index>.log contains the troughput measurements.
 	- Json iperf3 output (special format)
	- <test_unit_string> is the UTC time of the test as follow : YYYY-MM-DD-HHMM-SSZ
	- <index> equals 0,1,2 or 3. 4 qos tests are performed. To check which test was performed (UDP or TCP, direct or reverse), check the json fields.
	- **Requires** --qos option
	- **IMPORTANT :** In case of failure, the impacted result file has a "_failed" suffix, for instance : "qos_2018-10-25-0809-42Z_2_failed.log
 * trafficCapture_<browserName>_<test_unit_string>.log contains the pcap trace of the trafic seen during the operation of the browser (including all the loads).
	- PCAP format	
	- <browser_name> equals "ChromeQuic" or "ChromeNoQuic" (or anything indicated on the main_process.py header).
	- <test_unit_string> is the UTC time of the test as follow : YYYY-MM-DD-HHMM-SSZ
 * profile_<browserName>_<test_unit_string> is a folder containing all the profile of the browser.
	- Folder. Special format.
	- <browser_name> equals "ChromeQuic" or "ChromeNoQuic" (or anything indicated on the main_process.py header).
	- <test_unit_string> is the UTC time of the test as follow : YYYY-MM-DD-HHMM-SSZ
 * weather_<test_unit_string>.json contains the weather report for the test unit.
	- Json. Special format. See ICAO API.
	- <test_unit_string> is the UTC time of the test as follow : YYYY-MM-DD-HHMM-SSZ
 	- **Requires** : --weather option


