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
You need to find your own webpage on a GQUIC capable server somewhere in the internet.
Then, open **EACH** python script and complete the requested parameters between the *CONFIG* markers.

# Launch
Once configured, to launch test procedure :

```bash
$ sudo python3 main_process.py
```
