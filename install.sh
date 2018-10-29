#!/bin/bash
#
# QUXA is a QUIC User eXperience Assesment experiment tool
# 
# Copyright © 2018 CNES
# 
# This file is part of QUXA
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY, without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see http://www.gnu.org/licenses/.
#

# Install script of QUXA tool 
# Be aware that it is better to have a dedicated vm : 
# No cleaning script is available. 

# Author : Ludovic Thomas 


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
