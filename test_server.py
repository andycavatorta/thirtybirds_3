######################
### LOAD LIBS AND GLOBALS ###
######################

import importlib
import os
import sys
import time

import test_settings as settings

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
UPPER_PATH = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
#DEVICES_PATH = "%s/Hosts/" % (BASE_PATH )
#THIRTYBIRDS_PATH = "%s/thirtybirds_3" % (UPPER_PATH )

sys.path.append(BASE_PATH)
sys.path.append(UPPER_PATH)

from network.info import init as network_info_init
network_info = network_info_init()

import network.connection as network_connection
import network

def message_callback(msg):
    print "message_callback", msg

def status_callback(msg):
    print "status_callback", msg

network_connection.init(
        network_info.getHostName(), 
        network.CONNECTION_ROLE_CLIENT, 
        settings.Network.pubsub_pub_port, 
        network.DISCOVERY_METHOD_MULTICAST, 
        {
            "address":settings.Network.discovery_multicast_address,
            "port":settings.Network.discovery_multicast_port,
            "response_port":settings.Network.discovery_response_port
        },
        message_callback, 
        status_callback
    )

