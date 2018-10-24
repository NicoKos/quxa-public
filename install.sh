cd ~
sudo apt update
sudo apt install -y python3 python3-pip libiperf-dev git python3-matplotlib
sudo -E pip3 install --upgrade pip
sudo -E pip3 install selenium
sudo -E pip3 install psutil
sudo -E pip3 install mailjet_rest
sudo -E pip3 install numpy
cd ~
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb
wget https://chromedriver.storage.googleapis.com/2.40/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo cp chromedriver /usr/bin/
cd ~
rm chromedriver
rm chromedriver_linux64.zip
cd ~
git clone https://github.com/esnet/iperf.git
cd iperf
make clean
sudo ./configure
sudo make -j20
sudo make install
rm /usr/lib/x86_64-linux-gnu/*iperf*
ldconfig
cd ~
