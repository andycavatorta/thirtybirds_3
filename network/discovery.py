"""
The network discovery process returns the ip address of the remote host and its status as reachable == [ True | False ]

there are three types of discovery:
STATIC: We start with a supplied IP address and return the reachable status.
MULTICAST: We use ip multicast with a supplied ip group to call for or listen for connections
BROKER: When multicast is not available, we can use a remote broker with a supplied hostname or ip address

It is tempting to detect disconnection here at the socket level.
But in the larger Thirtybirds system, testing at the zmq/pubsub level tests the whole system.

"""
#########################################
######## IMPORTS, PATHS, GLOBALS ########
#########################################

import json
import socket
import struct
import sys
import threading
import time
import yaml
import zmq

import network

from thirtybirds_3.network.info import init as network_info_init
network_info = network_info_init()

from reports import reports
exceptions = reports.Exceptions() # is there a way for a module to sniff a reference to the file that imports it?

###############################
##### MULTICAST RESPONDER #####
###############################

class MulticastResponder(threading.Thread):
    def __init__(self, hostname, discovery_multicast_group, discovery_multicast_port, discovery_response_port, status_callback, heartbeat_interval):
        try:
            threading.Thread.__init__(self)
            self.hostname = hostname
            self.listener_port = discovery_multicast_port
            self.response_port = discovery_response_port
            self.multicast_group_address = discovery_multicast_group
            self.local_ip = network_info.get_local_ip()
            self.status_callback = status_callback
            self.heartbeat_interval = heartbeat_interval
            self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.receive_socket.bind((self.multicast_group_address, self.listener_port))
            self.membership_request = struct.pack("4sl", socket.inet_aton(self.multicast_group_address), socket.INADDR_ANY)
            self.receive_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.membership_request)
            self.remote_connection_timestamps_keyed_by_ip = {}
        except Exception as e:
            exceptions.report(sys.exc_info())   

    def respond_with_local_ip(self, remote_ip): # response sends the local IP to the remote device
        try:
            if remote_ip in self.remote_connection_timestamps_keyed_by_ip: # if we have heard from this host already
                if self.remote_connection_timestamps_keyed_by_ip[remote_ip] + (self.heartbeat_interval * 2) > time.time(): # if we have heard from this host recently
                    return # we good
            else:
                self.remote_connection_timestamps_keyed_by_ip[remote_ip] = time.time()
            context = zmq.Context()
            response_socket = context.socket(zmq.PAIR)
            response_socket.connect("tcp://%s:%s" % (remote_ip,self.response_port))
            response_socket.send_string(json.dumps({"ip":self.local_ip,"hostname":self.hostname}))
            response_socket.close()
        except Exception as e:
            exceptions.report(sys.exc_info())   
        
    def run(self):
        while True:
            try:
                message_json_encoded = self.receive_socket.recv(1024)
                message_json = message_json_encoded.decode()
                print(message_json)
                message_d = yaml.safe_load(message_json)
                print(message_d)
                remote_ip = message_d["ip"]
                message_d["status"] = "device_discovered"
                if self.status_callback:
                    self.status_callback(message_d)
                self.respond_with_local_ip(remote_ip)
            except Exception as e:
                exceptions.report(sys.exc_info())   

############################
##### MULTICAST CALLER #####
############################

class MulticastCallerSend(threading.Thread):
    def __init__(self, local_hostname, discovery_multicast_group, discovery_multicast_port, discovery_response_port, heartbeat_interval):
        try:
            threading.Thread.__init__(self)
            self.multicast_group_address = discovery_multicast_group
            self.listener_port = discovery_multicast_port
            self.multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
            self.heartbeat_interval = heartbeat_interval
            self.local_ip = network_info.get_local_ip()
            self.message_d = {"ip":self.local_ip,"hostname":local_hostname}
            self.message_json = json.dumps(self.message_d)
            self.active = True # active means actively calling. remote host has not yet responded.
        except Exception as e:
            exceptions.report(sys.exc_info())   
    def set_active(self,val):
        try:
            self.active = val
        except Exception as e:
            exceptions.report(sys.exc_info())   
    def run(self):
        while True:
            try:
                if self.active == True:
                    self.multicast_socket.sendto(self.message_json.encode(), (self.multicast_group_address, self.listener_port))
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                exceptions.report(sys.exc_info())   

class MulticastCallerReceive(threading.Thread):
    def __init__(self, discovery_multicast_group, discovery_multicast_port, discovery_response_port, status_callback, caller_send):
        try:
            threading.Thread.__init__(self)
            self.status_callback = status_callback
            self.caller_send = caller_send
            self.receive_port = discovery_response_port
            self.listen_context = zmq.Context()
            self.listen_socket = self.listen_context.socket(zmq.PAIR)
            self.listen_socket.bind("tcp://*:%d" % self.receive_port)
        except Exception as e:
            exceptions.report(sys.exc_info())   

    def run(self):
        while True:
            try:
                message_json = self.listen_socket.recv()
                message_d = yaml.safe_load(message_json)
                message_d["status"] = "device_discovered"
                self.caller_send.set_active(False)
                if self.status_callback:
                    self.status_callback(message_d)
            except Exception as e:
                exceptions.report(sys.exc_info())   

##########################
##### BROKER RESPONDER #####
##########################


#######################
##### BROKER CALLER #####
#######################


##########################
##### STATIC RESPONDER #####
##########################



#######################
##### STATIC CALLER #####
#######################



########################
##### TIDY WRAPPER #####
########################

class Discovery(): # creates a common interface for different discovery types
    def __init__(
            self,
            hostname,
            role,
            discovery_method,
            discovery_multicast_group,
            discovery_multicast_port,
            discovery_response_port,
            status_callback,
            heartbeat_interval,
            reporting_paramaters
        ):
        try:
            self.hostname = hostname
            self.role = role
            self.discovery_method = discovery_method
            self.discovery_multicast_group = discovery_multicast_group
            self.discovery_multicast_port = discovery_multicast_port
            self.discovery_response_port = discovery_response_port
            self.status_callback = status_callback
            self.heartbeat_interval = heartbeat_interval
            self.server_ip = ""
            self.status = "" 

            if role == network.DISCOVERY_ROLE_CALLER:
                if discovery_method == network.DISCOVERY_METHOD_MULTICAST:
                    self.caller_send = MulticastCallerSend(hostname, discovery_multicast_group, discovery_multicast_port, discovery_response_port,  heartbeat_interval)
                    self.caller_receive = MulticastCallerReceive(discovery_multicast_group, discovery_multicast_port, discovery_response_port, status_callback, self.caller_send)
                if discovery_method == network.DISCOVERY_METHOD_BROKER:
                    self.caller_send = BrokerCallerSend(hostname, discovery_multicast_group, discovery_multicast_port, discovery_response_port,  heartbeat_interval)
                    self.caller_receive = BrokerCallerReceive(discovery_multicast_group, discovery_multicast_port, discovery_response_port,  status_callback, self.caller_send)
                if discovery_method == network.DISCOVERY_METHOD_STATIC:
                    self.caller_send = StaticCallerSend(hostname, discovery_multicast_group, discovery_multicast_port, discovery_response_port,  heartbeat_interval)
                    self.caller_receive = StaticCallerReceive(discovery_multicast_group, discovery_multicast_port, discovery_response_port,  status_callback, self.caller_send)
                self.caller_send.start()
                self.caller_receive.start()

            if self.role == network.DISCOVERY_ROLE_RESPONDER:
                if discovery_method == network.DISCOVERY_METHOD_MULTICAST:
                    self.responder = MulticastResponder(hostname, discovery_multicast_group, discovery_multicast_port, discovery_response_port,  status_callback, heartbeat_interval)
                if discovery_method == network.DISCOVERY_METHOD_BROKER:
                    self.responder = BrokerResponder(hostname, discovery_multicast_group, discovery_multicast_port, discovery_response_port,  status_callback, heartbeat_interval)
                if discovery_method == network.DISCOVERY_METHOD_STATIC:
                    self.responder = StaticResponder(hostname, discovery_multicast_group, discovery_multicast_port, discovery_response_port,  status_callback, heartbeat_interval)
                self.responder.start()
        except Exception as e:
            exceptions.report(sys.exc_info())    

    def begin(self):
        try:
            self.caller_send.set_active(True)
        except Exception as e:
            exceptions.report(sys.exc_info())    
        

    def end(self):
        try:
            self.caller_send.set_active(False)
        except Exception as e:
            exceptions.report(sys.exc_info())

def init(
        hostname,
        role,
        discovery_method,
        discovery_multicast_group,
        discovery_multicast_port,
        discovery_response_port,
        status_callback,
        heartbeat_interval,
        reporting_paramaters,
        publish_to_topic
    ):

    reports.init(
        reporting_paramaters.app_name,
        reporting_paramaters.logfile_location,
        reporting_paramaters.level,
        reporting_paramaters.print_to_stdout,
        reporting_paramaters.log_to_file,
        reporting_paramaters.publish_to_dash,
        reporting_paramaters.publish_as_topic,
        publish_to_topic,
        __file__
        )

    return Discovery(
        hostname,
        role,
        discovery_method,
        discovery_multicast_group,
        discovery_multicast_port,
        discovery_response_port,
        status_callback,
        heartbeat_interval,
        reporting_paramaters
    )

