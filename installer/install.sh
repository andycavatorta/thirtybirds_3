# update Raspian or Ubuntu
sudo apt update
sudo apt upgrade

# install package managers
sudo apt install python-pip
sudo apt install git
apt install curl

# 
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
git clone git@github.com:andycavatorta/thirtybirds_3.git

# install python libs
sudo apt install hddtemp lm-sensors
sudo apt install python3-dev
sudo apt install libtool pkg-config build-essential autoconf automake

# install 0MQ
sudo pip3 install netifaces
sudo apt install python-netifaces

cd libsodium-1.0.3/
./configure
make
sudo make install
cd ..

cd zeromq-4.1.3/
./configure
make
sudo make install
cd ..

sudo ldconfig
sudo pip3 install pyzmq
pip3 install pyyaml
#sudo pip install mido
#sudo apt install libportmidi-dev
#sudo pip install enum34
#python setuptools

